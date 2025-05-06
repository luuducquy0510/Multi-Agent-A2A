from langchain_community.tools import DuckDuckGoSearchResults


def web_search_tool(topic: str) -> dict:
    """Perform an online web search to retrieve the latest information about the given topic."""
    search = DuckDuckGoSearchResults(
        output_format="list",
        max_results=50
        )
    a = search.invoke(f"""{topic}""")
    return {"Search Results": a}

