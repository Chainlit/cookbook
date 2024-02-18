from pathlib import Path
from typing import List
from langchain_openai import AzureOpenAIEmbeddings,AzureChatOpenAI
from dotenv import load_dotenv 
from langchain.schema import Document
from langchain_pinecone import Pinecone
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    PyMuPDFLoader,
)
import os
import uuid
from pinecone import Pinecone, ServerlessSpec
import chainlit as cl

chunk_size = 1024
chunk_overlap = 50
PDF_STORAGE_PATH = "./pdfs"

# Load environment variables
load_dotenv()

# OpenAI configuration
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_ADA_DEPLOYMENT_VERSION = os.getenv("AZURE_OPENAI_ADA_DEPLOYMENT_VERSION")
AZURE_OPENAI_CHAT_DEPLOYMENT_VERSION= os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_VERSION")
AZURE_OPENAI_ADA_EMBEDDING_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_ADA_EMBEDDING_DEPLOYMENT_NAME")
AZURE_OPENAI_ADA_EMBEDDING_MODEL_NAME = os.getenv("AZURE_OPENAI_ADA_EMBEDDING_MODEL_NAME")
AZURE_OPENAI_CHAT_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME")

# Pinecone configuration
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
index_name = 'primer'

#Initialize Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=1536,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws",region="us-west-2") 
    )

#Initialize Azure OpenAI embeddings
    
embeddings = AzureOpenAIEmbeddings(
deployment=AZURE_OPENAI_ADA_EMBEDDING_DEPLOYMENT_NAME,
model=AZURE_OPENAI_ADA_EMBEDDING_MODEL_NAME,
azure_endpoint=AZURE_OPENAI_ENDPOINT,
openai_api_key=AZURE_OPENAI_API_KEY,
openai_api_version=AZURE_OPENAI_ADA_DEPLOYMENT_VERSION
)
def process_pdfs(pdf_storage_path: str):
    pdf_directory = Path(pdf_storage_path)
    docs = []
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    
    # Load PDFs and split into documents
    for pdf_path in pdf_directory.glob("*.pdf"):
        loader = PyMuPDFLoader(str(pdf_path))
        documents = loader.load()
        docs += text_splitter.split_documents(documents)
    

    # Convert text to embeddings
    for doc in docs:
        embedding = embeddings.embed_query(doc.page_content)
        random_id = str(uuid.uuid4())
        #print (embedding)
        doc_search = pc.Index(index_name)
        #doc_search = Pinecone (doc_search, embeddings.embed_query, doc.page_content, random_id)
    
    # Store the vector in Pinecone index
        doc_search.upsert(vectors = [{"id": random_id, "values": embedding, "metadata": {"source": doc.page_content}}])
        print("Vector stored in Pinecone index successfully.")
    return doc_search

doc_search = process_pdfs(PDF_STORAGE_PATH)

welcome_message = "Welcome to the Chainlit Pinecone demo! Ask anything about documents you vectorized and stored in your Pinecone DB."
namespace = None

from langchain.memory import ChatMessageHistory, ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.vectorstores.pinecone import Pinecone
import pinecone

@cl.on_chat_start
async def start():
    await cl.Message(content=welcome_message).send()
    docsearch = Pinecone.from_existing_index(
        index_name=index_name, embedding=embeddings, namespace=namespace
    )

    message_history = ChatMessageHistory()

    memory = ConversationBufferMemory(
        memory_key="chat_history",
        output_key="answer",
        chat_memory=message_history,
        return_messages=True,
    )

    chain = ConversationalRetrievalChain.from_llm(
        llm = AzureChatOpenAI(
        api_key=AZURE_OPENAI_API_KEY,
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        api_version=AZURE_OPENAI_CHAT_DEPLOYMENT_VERSION,
        openai_api_type="azure",
        azure_deployment=AZURE_OPENAI_CHAT_DEPLOYMENT_NAME,
        streaming=True
        ),
        chain_type="stuff",
        retriever=docsearch.as_retriever(),
        memory=memory,
        return_source_documents=True,
    )
    cl.user_session.set("chain", chain)

@cl.on_message
async def main(message: cl.Message):
    chain = cl.user_session.get("chain")  # type: ConversationalRetrievalChain

    cb = cl.AsyncLangchainCallbackHandler()

    res = await chain.acall(message.content, callbacks=[cb])
    answer = res["answer"]
    source_documents = res["source_documents"]  # type: List[Document]

    text_elements = []  # type: List[cl.Text]

    if source_documents:
        for source_idx, source_doc in enumerate(source_documents):
            source_name = f"source_{source_idx}"
            # Create the text element referenced in the message
            text_elements.append(
                cl.Text(content=source_doc.page_content, name=source_name)
            )
        source_names = [text_el.name for text_el in text_elements]

        if source_names:
            answer += f"\nSources: {', '.join(source_names)}"
        else:
            answer += "\nNo sources found"

    await cl.Message(content=answer, elements=text_elements).send()