import os
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


index_name = "langchain-demo"

# Optional
namespace = None

embeddings = OpenAIEmbeddings()

welcome_message = "Welcome to the Chainlit Pinecone demo! Ask anything about documents you vectorized and stored in your Pinecone DB."


@cl.langchain_factory(use_async=True)
async def langchain_factory():
    await cl.Message(content=welcome_message).send()
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
async def process_response(res):
    answer = res["answer"]
    sources = res.get("sources", "").strip()  # Use the get method with a default value
    source_elements = []
    docs = res.get("source_documents", None)

    if docs:
        metadatas = [doc.metadata for doc in docs]
        # Get the source names from the metadata
        all_sources = [m["source"] for m in metadatas]

        if sources:
            found_sources = []
            # For each source mentioned by the LLM
            for source_index, source in enumerate(sources.split(",")):
                # Remove the period and any whitespace
                orig_source_name = source.strip().replace(".", "")
                # The name that will be displayed in the UI
                clean_source_name = f"source {source_index}"
                try:
                    # Find the mentioned source in the list of all sources
                    found_index = all_sources.index(orig_source_name)
                except ValueError:
                    continue
                # Get the text from the source document
                text = docs[found_index].page_content

                found_sources.append(clean_source_name)
                source_elements.append(cl.Text(content=text, name=clean_source_name))

            if found_sources:
                # Add the sources to the answer, referencing the text elements
                answer += f"\nSources: {', '.join(found_sources)}"
            else:
                answer += "\nNo sources found"

    # Send the answer and the text elements to the UI
    await cl.Message(content=answer, elements=source_elements).send()
