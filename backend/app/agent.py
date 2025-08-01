import os
from typing import TypedDict, List,Dict,Optional
from langchain.schema import Document
from langgraph.graph import StateGraph, END, START
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
import asyncio
import ast
from qdrant_client import QdrantClient, models
# from langchain_community.llms import SambaNova
from tavily import TavilyClient
from langchain_sambanova import ChatSambaNovaCloud
from .kb_manager import embed_documents # Reusing the embedder
from .guardrails import anonymize_pii, is_math_question, is_toxic_or_refusal
from dotenv import load_dotenv
from fastmcp.client.transports import StreamableHttpTransport
load_dotenv()
from .guardrails import (
    anonymize_pii, is_math_question, is_toxic_or_refusal,
    is_response_grounded, is_aligned_to_task
)
from .optimizer import MathTutor
import dspy
from fastmcp import Client as MCPClient
os.environ['SAMBANOVA_API_KEY'] = os.getenv("SAMBANOVA_API_KEY")
# --- State Definition ---
# class AgentState(TypedDict):
#     question: str
#     original_question: str
#     collection_name: str
#     context: List[Document]
#     answer: str
#     source: str # 'Knowledge Base' or 'Web Search'
class AgentState(TypedDict):
    original_question: str
    question: str
    collection_name: str
    is_math: bool
    context: List[Document]
    context_str: str
    answer: str
    source: str
    rejection_reason: Optional[str]


# --- Tool Initializations ---
# Use your specified LLM from SambaNova
# import os
# from google.colab import userdata
from dotenv import load_dotenv
from fastmcp.client.transports import StreamableHttpTransport
load_dotenv()

from fastmcp import Client as MCPClient
os.environ['SAMBANOVA_API_KEY'] = os.getenv("SAMBANOVA_API_KEY")
llm = ChatSambaNovaCloud(
    model="Llama-4-Maverick-17B-128E-Instruct",
    max_tokens=1024,
    temperature=0.1,
    top_p=0.01,
)
dspy.settings.configure(lm=llm)
OPTIMIZED_PROMPT_FILE = "app/optimized_prompt.json"
optimized_math_tutor = MathTutor()
IS_OPTIMIZED = False
if os.path.exists(OPTIMIZED_PROMPT_FILE):
    try:
        print("---AGENT: Loading optimized prompt from file.---")
        optimized_math_tutor.load(OPTIMIZED_PROMPT_FILE)
        IS_OPTIMIZED = True
    except Exception as e:
        print(f"---AGENT: Error loading optimized prompt: {e}. Using default.---")
else:
    print("---AGENT: No optimized prompt found. Using default templates.---")
# Your prompt templates
SYSTEM_TEMPLATE = """
You are a math tutoring assistant. Use ONLY the provided context to answer the question.
Your goal is to provide a clear, step-by-step solution.
If the context does not contain enough information to answer, state that you cannot answer with the given information.

Always structure your response in this format:
<thinking>
[Your step-by-step reasoning derived from the context]
</thinking>

[Final answer here]
"""

HUMAN_TEMPLATE = """
CONTEXT:
{context_str}
---------------------
Using ONLY the information from the context above, answer the question: {query}
"""

def unwrap_tool_result(resp):
    """Safely unwraps the content from a FastMCP tool call result object."""
    if hasattr(resp, "content") and resp.content:
        content_object = resp.content[0]
        if hasattr(content_object, "text"):
            try:
                # Use ast.literal_eval for safely evaluating a string containing a Python literal
                return ast.literal_eval(content_object.text)
            except (ValueError, SyntaxError):
                return content_object.text # Return raw text if it's not a literal
    return resp

def run_mcp_tool_sync(tool_name: str, params: Dict):
    """A helper to run async MCP tool calls from our synchronous LangGraph node."""
    async def run():
        # FIX: Create a transport object with the URL first
        transport = StreamableHttpTransport(url="http://localhost:8000/mcp")
        
        # FIX: Pass the transport object to the client, not the URL
        async with MCPClient(transport) as client:
            response = await client.call_tool(tool_name, params)
            return unwrap_tool_result(response)
    
    return asyncio.run(run())


# --- Agent Nodes ---

def retrieve_from_kb(state: AgentState):
    """Retrieves relevant documents from the Qdrant knowledge base."""
    print("---AGENT: Retrieving from Knowledge Base---")
    question = state["question"]
    collection_name = state["collection_name"]
    
    # Initialize client to the specific collection for this request
    qdrant_client = QdrantClient(path=f"./qdrant_data/{collection_name}")
    
    dense_vec, sparse_vec = embed_documents([question])
    
    # Perform a hybrid search
    
    results = qdrant_client.search(
        collection_name=collection_name,
        query_vector=("dense", dense_vec[0]),
        # You can add sparse vector to query as well if your qdrant version supports it well
        with_payload=True,
        limit=4,
        score_threshold=0.6 # Your threshold
    )
    print(results)
    
    retrieved_docs = [Document(page_content=point.payload.get("answer")) for point in results]
    print(f"Found {len(retrieved_docs)} documents in KB.")
    return {"context": retrieved_docs, "source": "Knowledge Base"}
def web_search_node(state: AgentState):
    """Node 4: Calls our custom MathSearchExplorer MCP server for web context."""
    print("---NODE: Calling local MathSearchExplorer MCP Server---")
    question = state["question"]
    
    try:
        # FIX: Call the 'search_math_concepts' tool on our custom MCP server
        search_results = run_mcp_tool_sync(
            tool_name="search_math_concepts",
            params={"query": question, "max_results": 3}
        )

        if not search_results:
            return {"context": [], "context_str": "", "source": "Web Search (No Results)"}

        # Format the results into the XML string for the LLM
        context_str = "<search_results>\n"
        for res in search_results:
            context_str += f"""  <result source="{res.get('url', '')}">
    <title>{res.get('title', '')}</title>
    <snippet>{res.get('snippet', '')}</snippet>
  </result>\n"""
        context_str += "</search_results>"
        
        web_docs = [Document(page_content=context_str)]
        
        return {"context": web_docs, "context_str": context_str, "source": "Web Search (Custom)"}

    except Exception as e:
        print(f"Error calling custom MCP server: {e}")
        return {"context": [], "context_str": "", "source": "Web Search Failed"}

# def generate_solution(state: AgentState):
#     """Generates a final answer using the LLM and the retrieved context."""
#     print(f"---AGENT: Generating solution using context from {state['source']}---")
#     question = state["question"]
#     context_docs = state["context"]
    
#     docs_content = "\n\n".join(doc.page_content for doc in context_docs)
    
#     # Format the prompt using your templates
#     full_prompt = f"{SYSTEM_TEMPLATE}\n\n{HUMAN_TEMPLATE.format(context_str=docs_content, query=question)}"
    
#     response = llm.invoke(full_prompt)
#     response=response.content
#     print(response)

#     # Output guardrail
#     if is_toxic_or_refusal(response):
#         print("---GUARDRAIL: Output is toxic or a refusal. Replacing with safe response.---")
#         response = "I am sorry, but I cannot provide an answer to that question."

#     return {"answer": response}


def generate_solution_node(state: AgentState):
    """
    Generates a final answer using the optimized DSPy model if available,
    otherwise falls back to the default manual prompt templates.
    """
    print(f"---AGENT: Generating solution using context from {state['source']}---")
    question = state["question"]
    context_str = state["context_str"]
    answer_content = ""

    # FIX: Conditional logic to choose the generation method
    if IS_OPTIMIZED:
        print("---AGENT: Using optimized DSPy prompt.---")
        try:
            response_obj = optimized_math_tutor(question=question, context=context_str)
            answer_content = response_obj.solution
        except Exception as e:
            print(f"---AGENT: Error during DSPy generation: {e}.---")
            answer_content = "I encountered an error while generating the solution."
    else:
        print("---AGENT: Using default templates.---")
        # This is your original, preferred logic
        full_prompt = f"{SYSTEM_TEMPLATE}\n\n{HUMAN_TEMPLATE.format(context_str=context_str, query=question)}"
        response_obj = llm.invoke(full_prompt)
        answer_content = response_obj.content

    print(f"Raw Response: {answer_content}")

    # --- Output Guardrails ---
    if is_toxic_or_refusal(answer_content):
        print("---GUARDRAIL: Output is toxic or a refusal. Replacing with safe response.---")
        answer_content = "I am sorry, but I cannot provide an answer to that question."
    elif not is_response_grounded(answer_content, context_str):
        print("---GUARDRAIL: Ungrounded response detected.---")
        answer_content = "I found some information, but I could not construct a reliable answer based on the provided context."
    elif not is_aligned_to_task(answer_content):
        print("---GUARDRAIL: Misaligned response detected.---")
        answer_content = "I was unable to generate a step-by-step solution. Please try rephrasing your question."
    
    return {"answer": answer_content}
# --- Conditional Edge ---

def should_use_web_search(state: AgentState):
    """The routing logic to decide between web search and generating an answer."""
    print("---AGENT: Deciding next step---")
    if not state["context"]:
        print("---DECISION: No context found. Routing to web_search.---")
        return "web_search"
    else:
        print("---DECISION: Context found. Routing to generate_solution.---")
        return "generate_solution"

# --- Graph Assembly ---

def get_agent_executor():
    """Compiles and returns the LangGraph agent executor."""
    graph_builder = StateGraph(AgentState)
    
    # Add all the nodes
    graph_builder.add_node("retrieve_from_kb", retrieve_from_kb)
    graph_builder.add_node("web_search", web_search_node)
    graph_builder.add_node("generate_solution", generate_solution_node)
    
    # The graph starts with KB retrieval
    graph_builder.add_edge(START, "retrieve_from_kb")
    
    # Add the conditional edge for routing
    graph_builder.add_conditional_edges(
        "retrieve_from_kb",
        should_use_web_search,
        {
            "web_search": "web_search",
            "generate_solution": "generate_solution",
        }
    )
    
    # Web search always leads to generation
    graph_builder.add_edge("web_search", "generate_solution")
    
    # After generation, the process ends
    graph_builder.add_edge("generate_solution", END)
    
    return graph_builder.compile()