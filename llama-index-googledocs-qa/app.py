import os
from llama_index import download_loader
from llama_index import (
    ServiceContext,
    VectorStoreIndex,
    LangchainEmbedding,
    PromptHelper,
    LLMPredictor,
)
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from langchain.chat_models import ChatOpenAI
from llama_index import (
    LLMPredictor,
    ServiceContext,
    StorageContext,
    load_index_from_storage,
)
from llama_index.callbacks.base import CallbackManager
import openai
import chainlit as cl


openai.api_key = os.environ.get("OPENAI_API_KEY")


## Function to load the index from storage or create a new one
@cl.cache  ## Allow to cache the function
def load_context():
    try:
        # Rebuild the storage context
        storage_context = StorageContext.from_defaults(
            persist_dir="./storage",
            callback_manager=CallbackManager([cl.LlamaIndexCallbackHandler()]),
        )
        # Load the index
        index = load_index_from_storage(
            storage_context, storage_context=storage_context
        )
    except:
        # Storage not found; create a new one
        GoogleDocsReader = download_loader("GoogleDocsReader")

        gdoc_ids = ["G-DOC-ID-1", "G-DOC-ID-2", "G-DOC-ID-3"]

        loader = GoogleDocsReader()
        documents = loader.load_data(document_ids=gdoc_ids)
        llm_predictor = LLMPredictor(
            llm=ChatOpenAI(
                temperature=0,
                model_name="gpt-3.5-turbo-16k",
                streaming=True,
            ),
        )

        prompt_helper = PromptHelper(
            context_window=4096,
            num_output=256,
            chunk_overlap_ratio=0.1,
            chunk_size_limit=None,
        )
        # embed_model = LangchainEmbedding(HuggingFaceEmbeddings())
        # node_parser = SimpleNodeParser(
        #     text_splitter=TokenTextSplitter(
        #                     chunk_size=300, ## Here is the new size for each document
        #                     chunk_overlap=20
        #     ),
        # ) ## (optional)
        service_context = ServiceContext.from_defaults(
            llm_predictor=llm_predictor,
            # embed_model=embed_model, ## (optional)
            # node_parser=node_parser, ## (optional)
            prompt_helper=prompt_helper,
            callback_manager=CallbackManager([cl.LlamaIndexCallbackHandler()]),
        )
        index = VectorStoreIndex.from_documents(
            documents, service_context=service_context
        )
        index.storage_context.persist("./storage")
    return index


@cl.on_chat_start
async def start():
    index = load_context()

    query_engine = index.as_query_engine(
        streaming=True,
        similarity_top_k=2,
    )

    cl.user_session.set("query_engine", query_engine)

    await cl.Message(author="Assistant", content="Hello ! How may I help you ? ").send()


@cl.on_message
async def main(message: cl.Message):
    query_engine = cl.user_session.get("query_engine")

    msg = cl.Message(content="", author="Assistant")

    res = query_engine.query(message.content)

    for text in res.response_gen:
        token = text
        await msg.stream_token(token)

    await msg.send()
