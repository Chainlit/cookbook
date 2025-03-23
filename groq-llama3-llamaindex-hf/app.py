from llama_index.core import StorageContext, ServiceContext, load_index_from_storage
from llama_index.core.callbacks.base import CallbackManager
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()
import chainlit as cl

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

try:
    # rebuild storage context
    storage_context = StorageContext.from_defaults(persist_dir="./storage_mini")
    # load index
    index = load_index_from_storage(storage_context)
except:
    documents = SimpleDirectoryReader("./data").load_data(show_progress=True)
    index = VectorStoreIndex.from_documents(documents)
    index.storage_context.persist(persist_dir="./storage_mini")


@cl.on_chat_start
async def factory():
    embed_model = HuggingFaceEmbedding(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    llm = Groq(model="llama3-70b-8192", api_key=GROQ_API_KEY)

    service_context = ServiceContext.from_defaults(
        embed_model=embed_model,
        llm=llm,
        callback_manager=CallbackManager([cl.LlamaIndexCallbackHandler()]),
    )
    chat_engine = index.as_chat_engine(service_context=service_context)

    cl.user_session.set("chat_engine", chat_engine)


@cl.on_message
async def main(message: cl.Message):
    chat_engine = cl.user_session.get("chat_engine")
    response = await cl.make_async(chat_engine.chat)(message.content)

    response_message = cl.Message(content="", author="Assistant")

    for token in response.response:
        await response_message.stream_token(token=token)

    await response_message.send()
