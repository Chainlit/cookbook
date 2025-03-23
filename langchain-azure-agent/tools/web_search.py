import os
import requests
from langchain.tools import tool
from pydantic import BaseModel, Field

# Add your Bing Search V7 subscription key and endpoint to your environment variables.
BING_SEARCH_API_KEY = os.getenv("BING_SEARCH_API_KEY")
BING_ENDPOINT = os.getenv("BING_SEARCH_ENDPOINT") + "v7.0/search"


class SearchInput(BaseModel):
    query: str = Field(
        description="Provide a concise keyword-based query. Examples: 'financial report 2023,' 'AI trends 2024.' Avoid vague terms like 'report' or full sentences."
    )
    mkt: str = Field(
        default="en-US",
        description="Specify the target market and language (e.g., 'en-US' for US English, 'fr-FR' for French in France). Defaults to 'en-US.'",
    )


@tool("web-search-tool", args_schema=SearchInput)
async def web_search(query: str, mkt: str = "en-US") -> str:
    """
    Use this tool, the web search tool to search for information on the web via the Bing Search API.

    If no results are found an empty list is returned.

    Example response:
    1. **[The Benefits of Renewable Energy](https://example.com/renewable-energy)**
    *Source*: [example.com](https://example.com/renewable-energy)
    *Snippet*: Renewable energy reduces carbon emissions and promotes sustainability. Key technologies include solar, wind, and hydro power.
    """
    params = {"q": query, "mkt": mkt, "count": 5}
    headers = {"Ocp-Apim-Subscription-Key": BING_SEARCH_API_KEY}

    # Call the API
    try:
        response = requests.get(BING_ENDPOINT, headers=headers, params=params)
        response.raise_for_status()

        search_results = response.json()

        # Get the webpages from the search results
        result = search_results.get("webPages", {}).get("value", [])

        return [
            {
                "title": webpage.get("name"),
                "url": webpage.get("url"),
                "source": webpage.get("displayUrl"),
                "snippet": webpage.get("snippet"),
            }
            for webpage in result
        ]

    except Exception:
        return {
            "response": "An error occurred during the search.",
            "instructions": "Notify user of the error and provide guidance on alternative steps.",
        }
