import os
import warnings
from tqdm import tqdm

from langchain_community.vectorstores.chroma import Chroma
from langchain_community.document_loaders import (PyPDFLoader,CSVLoader, UnstructuredMarkdownLoader,UnstructuredPowerPointLoader,DirectoryLoader)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings

warnings.simplefilter(action='ignore')
llm_model = "llama2"
def create_vector_database():
    
    pdfDirecLoader = DirectoryLoader("./files/", glob="*.pdf",loader_cls=PyPDFLoader)
    loadedDocuments = pdfDirecLoader.load()
    print(len(loadedDocuments))
    #print(loadedDocuments)
    
    
    textSplitter = RecursiveCharacterTextSplitter(chunk_size=1000,chunk_overlap=50)
    chunkedDocuments = textSplitter.split_documents(loadedDocuments)
   # print(len(chunkedDocuments))
   # print(type(chunkedDocuments))
   # print(chunkedDocuments[0])
    content = []
    metadatas = []
    for doc in chunkedDocuments:
        content.append(doc.page_content)
        metadatas.append(doc.metadata)
   # print(content[0],metadatas[0],content[1],metadatas[1])
    
    ollama_embeddings = OllamaEmbeddings(model=llm_model,show_progress=True)
    
    vectorDB = Chroma.from_texts(texts=content,embedding=ollama_embeddings,metadatas=metadatas,persist_directory="./data")
    vectorDB.persist()
    
if __name__ == "__main__":
    create_vector_database()
