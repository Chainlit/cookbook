import os
import chainlit as cl
from typing import List

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_community.document_loaders import (
    AzureAIDocumentIntelligenceLoader,
    BSHTMLLoader,
    PyPDFLoader,
    TextLoader,
    UnstructuredExcelLoader,
    UnstructuredPowerPointLoader,
    Docx2txtLoader,
)


class AsyncLoader:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            model_name="gpt-4o",
            chunk_size=50000,
            chunk_overlap=5000,
        )
        self.document_intelligence_endpoint = os.getenv(
            "DOCUMENT_INTELLIGENCE_ENDPOINT")
        self.document_intelligence_api_key = os.getenv(
            "DOCUMENT_INTELLIGENCE_API_KEY")
        self.api_model = "prebuilt-layout"
        self.mode = "markdown"

    async def aload(
        self, file_name: str, file_mime: str, file_path: str
    ) -> List[Document]:
        documents = []
        loader = self._get_loader(file_mime, file_path)
        docs = await cl.make_async(loader.load)()
        split_docs = await self.text_splitter.atransform_documents(docs)

        for doc in split_docs:
            doc.metadata["thread_id"] = cl.user_session.get("current_thread")
            doc.metadata["title"] = file_name
            documents.append(doc)

        return documents

    def _get_loader(self, file_mime: str, file_path: str):

        if file_mime in {"image/jpeg", "image/png", "image/bmp", "image/tiff"}:
            ep = self.document_intelligence_endpoint
            key = self.document_intelligence_api_key

            if ep and key:
                return AzureAIDocumentIntelligenceLoader(
                    api_endpoint=ep,
                    api_key=key,
                    file_path=file_path,
                    api_model=self.api_model,
                    mode=self.mode,
                )

            # Neither present → local mode doesn't support images
            if not ep and not key:
                raise ValueError(
                    "Images are not supported when using the local version.")

            # Exactly one missing → be explicit which one
            if not ep:
                raise ValueError(
                    "Azure Document Intelligence endpoint is missing.")
            if not key:
                raise ValueError(
                    "Azure Document Intelligence API key is missing.")

        if file_mime == "text/html":
            return BSHTMLLoader(file_path, open_encoding="utf-8")
        if file_mime == "text/plain":
            return TextLoader(file_path, autodetect_encoding=True)
        if file_mime == "application/pdf":
            return PyPDFLoader(file_path, extract_images=False, mode="single")
        if file_mime == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            return Docx2txtLoader(file_path)
        if file_mime == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
            return UnstructuredExcelLoader(file_path)
        if file_mime == "application/vnd.openxmlformats-officedocument.presentationml.presentation":
            return UnstructuredPowerPointLoader(file_path)
