from dataclasses import dataclass
from ddgs import DDGS


@dataclass
class Result:
    title: str
    url: str
    snippet: str


async def shallow(query: str, k: int = 5) -> list[Result]:
    """Search using DuckDuckGo and return top K results.

    Args:
        query: search query
        k: number of results to return

    Returns:
        list of Result(title, url, snippet)
    """
    ddgs = DDGS(timeout=10)
    try:
        results = ddgs.text(query, max_results=k)
        return [
            Result(title=r.get("title", ""), url=r.get("href", ""), snippet=r.get("body", ""))
            for r in results
        ]
    except Exception:
        return []
