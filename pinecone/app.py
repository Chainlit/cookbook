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


@cl.on_chat_start
async def start():
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

    cl.user_session.set("chain", chain)


@cl.on_message
async def main(message):
    chain = cl.user_session.get("chain")  # type: RetrievalQAWithSourcesChain

    cb = cl.AsyncLangchainCallbackHandler(
        stream_final_answer=True, answer_prefix_tokens=["FINAL", "ANSWER"]
    )
    cb.answer_reached = True

    res = await chain.acall(message, callbacks=[cb])
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
                source_name = source.strip().replace(".", "")
                # Get the index of the source
                try:
                    index = all_sources.index(source_name)
                except ValueError:
                    continue
                text = docs[index].page_content
                found_sources.append(source_name)
                # Create the text element referenced in the message
                source_elements.append(cl.Text(content=text, name=source_name))

            if found_sources:
                # Add the sources to the answer, referencing the text elements
                answer += f"\nSources: {', '.join(found_sources)}"
            else:
                answer += "\nNo sources found"

    if cb.has_streamed_final_answer:
        cb.final_stream.elements = source_elements
        await cb.final_stream.update()
    else:
        await cl.Message(content=answer, elements=source_elements).send()
