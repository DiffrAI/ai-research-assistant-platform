"""Initialize and expose available tools for the agent."""

from langchain_core.tools import BaseTool
from app import settings

# Import DuckDuckGo tool always
from .duckduckgo_search_tool import DUCKDUCKGO_SEARCH_TOOL

# Conditionally import Tavily tool only if needed
if settings.SEARCH_PROVIDER.lower() == "tavily":
    from .tavily_search_tool import TAVILY_SEARCH_TOOL
    SEARCH_TOOL: BaseTool = TAVILY_SEARCH_TOOL
else:
    SEARCH_TOOL: BaseTool = DUCKDUCKGO_SEARCH_TOOL

TOOLS: list[BaseTool] = [SEARCH_TOOL]

__all__ = ["TOOLS", "SEARCH_TOOL", "DUCKDUCKGO_SEARCH_TOOL"]
# Only export TAVILY_SEARCH_TOOL if imported
if settings.SEARCH_PROVIDER.lower() == "tavily":
    __all__.append("TAVILY_SEARCH_TOOL")
