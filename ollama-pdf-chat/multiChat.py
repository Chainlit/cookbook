import os
import time
import chainlit as cl
import warnings
from langchain_community.vectorstores.chroma import Chroma
from langchain_community.document_loaders import (PyPDFLoader,DirectoryLoader)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from langchain.chains import ConversationalRetrievalChain
from langchain_community.chat_models.ollama import ChatOllama
from langchain.memory import ChatMessageHistory,ConversationBufferMemory

llmmodel = os.getenv("LLM_MODEL", "llama2")
llmmodel = "llama2"
print(llmmodel)

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000,chunk_overlap=50)

@cl.on_chat_start 
async def on_chat_start():
    warnings.simplefilter(action='ignore')
    ollama_embeddings = OllamaEmbeddings(model=llmmodel,show_progress=True)
    vectorDB = Chroma(persist_directory="./data",embedding_function=ollama_embeddings)
    
    msg = cl.Message(content=f"Processing Started ...")
    time.sleep(3)
    await msg.send()
    
    if not os.path.exists("./files"):
        os.makedirs("./files")
    if not os.path.exists("./data"):
        os.makedirs("./data")
        pdfDirecLoader = DirectoryLoader("./files/", glob="*.pdf",loader_cls=PyPDFLoader)
        loadedDocuments = pdfDirecLoader.load()
        chunkedDocuments = text_splitter.split_documents(loadedDocuments)
        content = []
        metadatas = []
        for doc in chunkedDocuments:
            content.append(doc.page_content)
            metadatas.append(doc.metadata)
        vectorDB = Chroma.from_texts(texts=content,embedding=ollama_embeddings,metadatas=metadatas,persist_directory="./data")
        vectorDB.persist()
    
    vectorDB = Chroma(persist_directory="./data",embedding_function=ollama_embeddings)
    
    messageHistory = ChatMessageHistory()
    
    memory = ConversationBufferMemory(memory_key="chat_history",output_key="answer",
    chat_memory=messageHistory,                                      return_messages=True)
    
    chain = ConversationalRetrievalChain.from_llm(ChatOllama(model=llmmodel,temperature=0.2,streaming=True),chain_type="stuff",retriever=vectorDB.as_retriever(mmr=True),
    memory=memory,
    return_source_documents=True,)
    
    msg.content = f"Processing Complete..."
    await msg.update()
    
    cl.user_session.set("chain",chain)

@cl.on_message
async def main(message: cl.Message):
    chain = cl.user_session.get("chain")  # type: ConversationalRetrievalChain
    cb = cl.AsyncLangchainCallbackHandler()

    res = await chain.acall(message.content, callbacks=[cb])
    answer = res["answer"]
    source_documents = res["source_documents"]  

    text_elements = []  

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

    
        
