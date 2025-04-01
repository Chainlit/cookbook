import os
from azure.search.documents.indexes.models import (
    SearchableField,
    SearchField,
    SearchFieldDataType,
    SimpleField,
)
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from langchain_community.vectorstores.azuresearch import AzureSearch


class AzureServices:
    """
    Class to encapsulate Azure Search and OpenAI services configuration and functionality.
    """

    def __init__(self):
        # Azure Search service constants
        self.azure_search_service_endpoint = os.environ.get(
            "AZURE_SEARCH_SERVICE_ENDPOINT"
        )
        self.azure_search_api_key = os.environ.get("AZURE_SEARCH_API_KEY")

        # Azure OpenAI service constants
        self.azure_openai_chat_deployment_name = os.environ.get(
            "AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"
        )
        self.azure_openai_embeddings_deployment_name = os.environ.get(
            "AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT_NAME"
        )
        self.azure_openai_api_version = os.environ.get("AZURE_OPENAI_API_VERSION")
        self.azure_openai_api_key = os.environ.get("AZURE_OPENAI_API_KEY")
        self.azure_openai_endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")

        # Initialize the Azure Chat OpenAI model
        self.model = AzureChatOpenAI(
            azure_deployment=self.azure_openai_chat_deployment_name,
            openai_api_version=self.azure_openai_api_version,
            azure_endpoint=self.azure_openai_endpoint,
            api_key=self.azure_openai_api_key,
            model_name="gpt-4o",
            temperature=0,
            streaming=True,
        )

        # Initialize the Azure OpenAI Embeddings model
        self.embeddings = AzureOpenAIEmbeddings(
            azure_deployment=self.azure_openai_embeddings_deployment_name,
            openai_api_version=self.azure_openai_api_version,
            azure_endpoint=self.azure_openai_endpoint,
            api_key=self.azure_openai_api_key,
            model="text-embedding-3-large",
        )

        # Define fields for user-upload index
        self.uploaded_files_fields = [
            SimpleField(
                name="id", type=SearchFieldDataType.String, key=True, filterable=True
            ),
            SearchableField(
                name="content", type=SearchFieldDataType.String, searchable=True
            ),
            SearchField(
                name="content_vector",
                type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                searchable=True,
                vector_search_dimensions=len(self.embeddings.embed_query("Text")),
                vector_search_profile_name="myHnswProfile",
            ),
            SearchableField(
                name="metadata", type=SearchFieldDataType.String, searchable=True
            ),
            SearchableField(
                name="title", type=SearchFieldDataType.String, searchable=True
            ),
            SimpleField(
                name="thread_id",
                type=SearchFieldDataType.String,
                filterable=True,
                searchable=True,
            ),
        ]

        # Initialize Azure Search vector store for user uploads
        self.uploaded_files_vector_store = AzureSearch(
            azure_search_endpoint=self.azure_search_service_endpoint,
            azure_search_key=self.azure_search_api_key,
            index_name="uploaded-files-idx",
            embedding_function=self.embeddings.embed_query,
            fields=self.uploaded_files_fields,
        )

        # Define fields for RAG index
        self.rag_idx_fields = [
            SimpleField(
                name="id", type=SearchFieldDataType.String, key=True, filterable=True
            ),
            SearchableField(
                name="content", type=SearchFieldDataType.String, searchable=True
            ),
            SearchField(
                name="content_vector",
                type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                searchable=True,
                vector_search_dimensions=len(self.embeddings.embed_query("Text")),
                vector_search_profile_name="myHnswProfile",
            ),
            SearchableField(
                name="metadata", type=SearchFieldDataType.String, searchable=True
            ),
            SearchableField(
                name="title", type=SearchFieldDataType.String, searchable=True
            ),
            SimpleField(name="url", type=SearchFieldDataType.String, filterable=True),
        ]

        # Initialize Azure Search vector store for RAG index
        self.rag_vector_store = AzureSearch(
            azure_search_endpoint=self.azure_search_service_endpoint,
            azure_search_key=self.azure_search_api_key,
            index_name="rag-idx",
            embedding_function=self.embeddings.embed_query,
            fields=self.rag_idx_fields,
        )
