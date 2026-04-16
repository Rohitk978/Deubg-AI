"""
Web search tool — wraps Tavily search API with:
- Graceful fallback when API key is missing
- Result deduplication
- Query sanitization
- Structured output formatting
"""
import os
import re
from dotenv import load_dotenv

load_dotenv()

_tavily_client = None

def _get_client():
    global _tavily_client
    if _tavily_client is not None:
        return _tavily_client

    api_key = os.getenv("TAVILY_API_KEY", "")
    if not api_key:
        return None

    try:
        from langchain_tavily import TavilySearch
        _tavily_client = TavilySearch(
            tavily_api_key=api_key,
            max_results=5,
        )
        return _tavily_client
    except Exception as e:
        print(f"[WebSearch] Failed to init Tavily client: {e}")
        return None


def _sanitize_query(query: str) -> str:
    """Trim and clean the search query."""
    query = re.sub(r"\[.*?\]", "", query)   
    query = re.sub(r"`.*?`", "", query)     
    query = " ".join(query.split())         
    return query[:200].strip()              


def _format_results(results: list) -> str:
    """Format search results into clean readable text."""
    if not results:
        return "No results found."

    seen_urls = set()
    formatted = []

    for r in results:
        url = r.get("url", "")
        title = r.get("title", "No title").strip()
        content = r.get("content", "").strip()[:400]   

        if url in seen_urls:
            continue
        seen_urls.add(url)

        formatted.append(
            f"{title}\n"
            f"URL:{url}\n"
            f"{content}"
        )

    return "\n\n---\n\n".join(formatted)


def websearch(query: str) -> str:
    """
    Search the web for information about a bug or error.
    Returns formatted results or a fallback message.
    """
    client = _get_client()

    if client is None:
        return (
            "Web search unavailable - TAVILY_API_KEY not set. "
            "Add your Tavily API key to .env to enable web search. "
            "Falling back to LLM-only fix."
        )

    clean_query = _sanitize_query(query)
    print(f"[WebSearch] Query: {clean_query!r}")

    try:
        results = client.invoke({"query": clean_query})
        formatted = _format_results(results)
        print(f"Got {len(results)} result.")
        return formatted

    except Exception as e:
        print(f"Error: {e}")
        return f"Web search failed: {str(e)}. Falling back to LLM-only fix."
