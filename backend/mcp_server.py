# import os
# from typing import Dict, List
# from fastmcp import FastMCP
# from tavily import TavilyClient
# from dotenv import load_dotenv
# # --- Configuration ---
# load_dotenv()

# TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY")
# if not TAVILY_API_KEY:
#     raise ValueError("Please set the TAVILY_API_KEY environment variable.")

# # Initialize the underlying search client and the MCP server
# tavily = TavilyClient(api_key=TAVILY_API_KEY)
# mcp = FastMCP(name="MathSearchExplorer")
# print("✅ MathSearchExplorer server initialized.")


# # --- Dynamic Resource: Suggested Math search domains ---
# @mcp.resource("resource://math/trusted_sites")
# def trusted_math_sites() -> List[str]:
#     """Provides a list of reliable websites for mathematical content."""
#     return [
#         "khanacademy.org",
#         "mathisfun.com",
#         "brilliant.org",
#         "wolframalpha.com",
#         "mathworld.wolfram.com",
#         "purplemath.com",
#         "wikipedia.org"
#     ]

# print(f"✅ Resource 'resource://math/trusted_sites' registered.")


# # --- Tool: Search trusted math sites ---
# @mcp.tool(annotations={"title": "Search Math Concepts"})
# def search_math_concepts(query: str, max_results: int = 5) -> List[Dict]:
#     """
#     Searches trusted academic and educational sites for math concepts,
#     formulas, and step-by-step explanations.
#     """
#     print(f"Executing tool 'search_math_concepts' for query: {query}")
#     resp = tavily.search(
#         query=query,
#         search_depth="advanced",
#         max_results=max_results,
#         include_domains=trusted_math_sites() # Use our resource for high-quality results
#     )

#     return [
#         {"title": r["title"].strip(), "url": r["url"], "snippet": r.get("content", "")} 
#         for r in resp.get("results", [])
#     ]


# # --- Tool: Get a direct answer from WolframAlpha ---
# @mcp.tool(annotations={"title": "Calculate or Define with WolframAlpha"})
# def get_wolframalpha_result(query: str) -> str:
#     """
#     Gets a direct answer, calculation, or definition for a specific query
#     using WolframAlpha via Tavily's Q&A search. Best for specific formulas
#     or direct computations like 'derivative of x^2'.
#     """
#     print(f"Executing tool 'get_wolframalpha_result' for query: {query}")
#     # We use qna_search for a direct, synthesized answer
#     return tavily.qna_search(query=f"site:wolframalpha.com {query}")


# print("✅ Tools 'Search Math Concepts' and 'Get WolframAlpha Result' registered.")

# # --- Main execution block to run the server ---
# if __name__ == "__main__":
#     print("\n🚀 Starting MathSearchExplorer Server...")
#     # This will run the server, typically on http://localhost:8000/mcp
#     mcp.run(transport="http")


import os
from typing import Dict, List
from fastmcp import FastMCP
from tavily import TavilyClient
from dotenv import load_dotenv

# --- Configuration ---
load_dotenv()

TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY")
if not TAVILY_API_KEY:
    raise ValueError("Please set the TAVILY_API_KEY environment variable.")

tavily = TavilyClient(api_key=TAVILY_API_KEY)
mcp = FastMCP(name="MathSearchExplorer")
print("✅ MathSearchExplorer server initialized.")


# --- FIX: Converted the resource into a simple Python constant list ---
# A tool can use a constant directly, but it cannot "call" a resource on the same server.
TRUSTED_MATH_SITES: List[str] = [
    "khanacademy.org",
    "mathisfun.com",
    "brilliant.org",
    "wolframalpha.com",
    "mathworld.wolfram.com",
    "purplemath.com",
    "wikipedia.org"
]

print(f"✅ Loaded {len(TRUSTED_MATH_SITES)} trusted math sites as a constant.")


# --- Tool: Search trusted math sites ---
@mcp.tool(annotations={"title": "Search Math Concepts"})
def search_math_concepts(query: str, max_results: int = 5) -> List[Dict]:
    """
    Searches trusted academic and educational sites for math concepts,
    formulas, and step-by-step explanations.
    """
    print(f"Executing tool 'search_math_concepts' for query: {query}")
    resp = tavily.search(
        query=query,
        search_depth="advanced",
        max_results=max_results,
        # FIX: Use the constant list directly here.
        include_domains=TRUSTED_MATH_SITES
    )

    return [
        {"title": r["title"].strip(), "url": r["url"], "snippet": r.get("content", "")}
        for r in resp.get("results", [])
    ]


# --- Tool: Get a direct answer from WolframAlpha ---
@mcp.tool(annotations={"title": "Calculate or Define with WolframAlpha"})
def get_wolframalpha_result(query: str) -> str:
    """
    Gets a direct answer, calculation, or definition for a specific query
    using WolframAlpha via Tavily's Q&A search. Best for specific formulas
    or direct computations like 'derivative of x^2'.
    """
    print(f"Executing tool 'get_wolframalpha_result' for query: {query}")
    return tavily.qna_search(query=f"site:wolframalpha.com {query}")


print("✅ Tools 'Search Math Concepts' and 'Get WolframAlpha Result' registered.")

# --- Main execution block to run the server ---
if __name__ == "__main__":
    print("\n🚀 Starting MathSearchExplorer Server...")
    mcp.run(transport="http")
