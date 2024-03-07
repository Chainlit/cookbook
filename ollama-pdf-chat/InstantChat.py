import os
from typing import List
from langchain_community.document_loaders import PyPDFLoader

from langchain.embeddings.ollama import OllamaEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores.chroma import Chroma
from langchain.chains import (
    ConversationalRetrievalChain,
)
from langchain_community.chat_models import ChatOllama

from langchain.docstore.document import Document
from langchain.memory import ChatMessageHistory, ConversationBufferMemory


import chainlit as cl
from dotenv import load_dotenv
load_dotenv(dotenv_path=".env",verbose=True)

llm_model = os.getenv("LLM_MODEL", "gemma")
print(f"LLM_MODEL value: {llm_model}")
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)


@cl.on_chat_start
async def on_chat_start():
    files = None

    # Wait for the user to upload a file
    while files == None:
        files = await cl.AskFileMessage(
            content="Please upload a text file or PDF  to begin!",
            accept=["text/plain","application/pdf"],
            max_size_mb=20,
            timeout=180,
        ).send()
    
    file = files[0]


    msg = cl.Message(content=f"Processing `{file.name}`...", disable_feedback=True)
    await msg.send()
    if(file.type == "text/plain"):
        with open(file.path, "r", encoding="utf-8") as f:
            text = f.read()

        # Split the text into chunks
        texts = text_splitter.split_text(text)

        # Create a metadata for each chunk
        metadatas = [{"source": f"{i}-pl"} for i in range(len(texts))]

        # Create a Chroma vector store
        embeddings = OllamaEmbeddings(temperature=0.3,top_k=20,show_progress=True, model=llm_model)
        docsearch = await cl.make_async(Chroma.from_texts)(
            texts, embeddings, metadatas=metadatas
        )
    elif file.type == "application/pdf":
        # Load the PDF file
        loader = PyPDFLoader(file.path)
        embeddings = OllamaEmbeddings(temperature=0.3,top_k=20,show_progress=True, model=llm_model)
        
        # Extract the text content
        texts  = text_splitter.split_documents(loader.load())
         # Extract the metadata
        textCollection = []
        metadatas = []
        for text in texts:
            textCollection.append(text.page_content)
            metadatas.append(text.metadata)
        docsearch = await cl.make_async(Chroma.from_texts)(
            textCollection, embeddings, metadatas=metadatas
        )
        
       

    message_history = ChatMessageHistory()

    memory = ConversationBufferMemory(
        memory_key="chat_history",
        output_key="answer",
        chat_memory=message_history,
        return_messages=True,
    )

    # Create a chain that uses the Chroma vector store
    chain = ConversationalRetrievalChain.from_llm(
        ChatOllama(model_name=llm_model, temperature=0.2, streaming=True),
        chain_type="stuff",
        retriever=docsearch.as_retriever(),
        memory=memory,
        return_source_documents=True,
        
    )

    # Let the user know that the system is ready
    msg.content = f"Processing `{file.name}` done. You can now ask questions! We are using the {llm_model} model."
    await msg.update()

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
