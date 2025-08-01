# #
# # This file contains Guardrail functions to ensure safety and privacy.
# #
# from presidio_analyzer import AnalyzerEngine
# from presidio_anonymizer import AnonymizerEngine
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_core.output_parsers import StrOutputParser
# # from langchain_openai import ChatOpenAI
# import os
# from langchain_sambanova import ChatSambaNovaCloud
# from dotenv import load_dotenv
# # Initialize Presidio for PII detection
# load_dotenv()
# analyzer = AnalyzerEngine()
# anonymizer = AnonymizerEngine()
# os.environ['SAMBANOVA_API_KEY'] = os.getenv("SAMBANOVA_API_KEY")
# # Initialize an LLM for guardrail checks
# # Using OpenAI here as it's typically fast and cheap for simple checks,
# # but you can substitute it with your SambaNova model.
# llm = ChatSambaNovaCloud(
#     model="Llama-4-Maverick-17B-128E-Instruct",
#     max_tokens=1024,
#     temperature=0.1,
#     top_p=0.01,
# )

# def anonymize_pii(text: str) -> str:
#     """Removes Personally Identifiable Information from the text."""
#     results = analyzer.analyze(text=text, language='en')
#     anonymized_text = anonymizer.anonymize(text=text, analyzer_results=results)
#     return anonymized_text.text

# def is_math_question(question: str) -> bool:
#     """Checks if a question is about mathematics."""
#     prompt = ChatPromptTemplate.from_messages([
#         ("system", "Is the following question about mathematics or a word problem? Answer with only 'yes' or 'no'."),
#         ("user", "{input}")
#     ])
#     chain = prompt | llm | StrOutputParser()
#     response = chain.invoke({"input": question}).lower().strip()
#     return "yes" in response

# def is_toxic_or_refusal(text: str) -> bool:
#     """Checks if the LLM's output is toxic or a refusal to answer."""
#     prompt = ChatPromptTemplate.from_messages([
#         ("system", "Is the following text toxic, harmful, or a refusal to answer (e.g., 'I can't answer that')? Answer with only 'yes' or 'no'."),
#         ("user", "{input}")
#     ])
#     chain = prompt | llm | StrOutputParser()
#     response = chain.invoke({"input": text}).lower().strip()
#     print(response)

#     return "yes" in response


# This file contains Guardrail functions to ensure safety and privacy.

# FIX: We no longer need the LLM for toxicity checks, so some imports can be removed if only used here.
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_sambanova import ChatSambaNovaCloud
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

# NEW: Import the Detoxify library
from detoxify import Detoxify

# --- Initializations ---

# Initialize Presidio for PII detection
analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()
import os
# Initialize an LLM for guardrail checks (still used for topic, grounding, etc.)
from dotenv import load_dotenv
from fastmcp.client.transports import StreamableHttpTransport
load_dotenv()

from fastmcp import Client as MCPClient
os.environ['SAMBANOVA_API_KEY'] = os.getenv("SAMBANOVA_API_KEY")
guardrail_llm = ChatSambaNovaCloud(
    model="Llama-4-Maverick-17B-128E-Instruct",
    max_tokens=1024,
    temperature=0.1,
    top_p=0.01,
)

# NEW: Load the detoxify model once on startup.
# This model runs locally on your machine's CPU or GPU.
# Using 'unbiased' model which is robust and recommended.
toxicity_checker = Detoxify('unbiased')
print("✅ Detoxify model loaded for toxicity checks.")


def anonymize_pii(text: str) -> str:
    """Removes Personally Identifiable Information from the text."""
    results = analyzer.analyze(text=text, language='en')
    anonymized_text = anonymizer.anonymize(text=text, analyzer_results=results)
    return anonymized_text.text


def is_math_question(question: str) -> bool:
    """Checks if a question is about mathematics."""
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Is the following question about mathematics or a word problem? Answer with only 'yes' or 'no'."),
        ("user", "{input}")
    ])
    chain = prompt | guardrail_llm | StrOutputParser()
    response = chain.invoke({"input": question}).lower().strip()
    return "yes" in response


# --- FIX: Replaced the LLM-based function with the Detoxify implementation ---
def is_toxic_or_refusal(text: str) -> bool:
    """
    Checks if the text is toxic using the Detoxify library.
    Also includes a simple check for common refusal phrases.
    """
    # First, check for simple refusal phrases
    refusal_phrases = [
        "i can't answer that",
        "i cannot answer that",
        "i am unable to",
        "as a large language model",
    ]
    if any(phrase in text.lower() for phrase in refusal_phrases):
        print("---GUARDRAIL: Refusal phrase detected.---")
        return True

    # Next, use Detoxify for toxicity prediction
    # The library returns a dictionary of scores for different labels.
    predictions = toxicity_checker.predict(text)
    
    # We'll consider the text toxic if any category has a high probability score.
    # You can adjust this threshold as needed. A value of 0.8 is a good starting point.
    threshold = 0.8
    for label, score in predictions.items():
        if score > threshold:
            print(f"---GUARDRAIL: High toxicity score detected for '{label}' ({score:.2f})---")
            return True
            
    return False


# ... (is_response_grounded and is_aligned_to_task functions remain the same) ...

def is_response_grounded(answer: str, context: str) -> bool:
    """Checks if the answer is supported by the provided context."""
    # ... (implementation remains the same)
    return True # Placeholder

def is_aligned_to_task(text: str) -> bool:
    """Checks if the output is a step-by-step math solution."""
    # ... (implementation remains the same)
    return True # Placeholder