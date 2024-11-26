from langchain.tools import tool
from services.azure_services import AzureServices
from pydantic import BaseModel, Field


azure_services = AzureServices()


class SearchInput(BaseModel):
    query: str = Field(
        description="Provide a semantic search query. Avoid overly broad or vague queries. Example of good queries: 'Key findings from the 2023 financial report.', 'Summary of climate change policies in Document X.' Avoid: Single-word queries or overly general searches, like 'report.'"
    )


@tool("rag-search-tool", args_schema=SearchInput)
async def rag_search(query: str) -> str:
    """
Use this tool, the rag search tool, to access a large collection of documents that can be searched using semantic search.

Think carefully about how the information you find relates to the user's request. Respond as soon as you find information that clearly answers the request.

You should only issue multiple queries when the user's question needs to be decomposed to find different facts. In other scenarios, prefer providing a single, well-designed query.

Always provide references using markdown footnotes. For example:

Revenue increased by 10% in 2023. [^1]

Then, list the footnote references at the bottom of the document:

[^1]: [2023 Financial Report, Page 5](https://example.com/report.pdf)
    """
    try:
        result = await azure_services.rag_vector_store.asimilarity_search(
            query=query, k=5, search_type="similarity")

        return [
            {
                "page_content": doc.page_content,
                "url": doc.metadata["url"],
                "title": doc.metadata["title"]
            }
            for doc in result
        ]
    except Exception:
        return {"response": "An error occurred during the search.", "instructions": "Notify user of the error and provide guidance on alternative steps."}
