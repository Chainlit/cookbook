import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Pinecone
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.chat_models import ChatOpenAI
import pinecone
import chainlit as cl

pinecone.init(
    api_key=os.environ.get("PINECONE_API_KEY"),
    environment=os.environ.get("PINECONE_ENV"),
)

index_name = "test"
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
embeddings = OpenAIEmbeddings()

index_name = "langchain-demo"
# Optional
namespace = None

welcome_message = "Welcome to the Chainlit Pinecone demo! Ask anything about documents you vectorized and stored in your Pinecone DB."


@cl.langchain_factory
def langchain_factory():
    cl.Message(content=welcome_message).send()
    docsearch = Pinecone.from_existing_index(
        index_name=index_name, embedding=embeddings, namespace=namespace
    )

    chain = RetrievalQAWithSourcesChain.from_chain_type(
        ChatOpenAI(temperature=0, streaming=True),
        chain_type="stuff",
        retriever=docsearch.as_retriever(max_tokens_limit=4097),
        return_source_documents=True,
    )
    return chain


@cl.langchain_postprocess
def process_response(res):
    answer = res["answer"]
    sources = res.get("sources", "").strip()  # Use the get method with a default value
    source_elements = []
    docs = res.get("source_documents", None)

    if docs:
        metadatas = [doc.metadata for doc in docs]
        all_sources = [m["source"] for m in metadatas]

        if sources:
            found_sources = []

            for source_index, source in enumerate(sources.split(",")):
                orig_source_name = source.strip().replace(".", "")
                clean_source_name = f"source {source_index}"
                try:
                    found_index = all_sources.index(orig_source_name)
                except ValueError:
                    continue
                text = docs[found_index].page_content
                found_sources.append(clean_source_name)
                source_elements.append(cl.Text(text=text, name=clean_source_name))

            if found_sources:
                answer += f"\nSources: {', '.join(found_sources)}"
            else:
                answer += "\nNo sources found"

    cl.Message(content=answer, elements=source_elements).send()
