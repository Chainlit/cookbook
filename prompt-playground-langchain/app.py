import os

from langchain.llms.huggingface_hub import HuggingFaceHub
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from langchain.schema.runnable import Runnable
from langchain.schema.runnable.config import RunnableConfig

from chainlit.playground.config import add_llm_provider
from chainlit.playground.providers.langchain import LangchainGenericProvider
import chainlit as cl

# Instantiate the LLM
llm = HuggingFaceHub(
    model_kwargs={"max_length": 500},
    repo_id="google/flan-t5-xxl",
    huggingfacehub_api_token=os.environ["HUGGINGFACEHUB_API_TOKEN"],
)

# Add the LLM provider
add_llm_provider(
    LangchainGenericProvider(
        # It is important that the id of the provider matches the _llm_type
        id=llm._llm_type,
        # The name is not important. It will be displayed in the UI.
        name="HuggingFaceHub",
        # This should always be a Langchain llm instance (correctly configured)
        llm=llm,
        # If the LLM works with messages, set this to True
        is_chat=False,
    )
)


@cl.on_chat_start
async def on_chat_start():
    prompt = ChatPromptTemplate.from_messages(
        [
            ("human", "{question}"),
        ]
    )
    runnable = prompt | llm | StrOutputParser()
    cl.user_session.set("runnable", runnable)


@cl.on_message
async def on_message(message: cl.Message):
    runnable = cl.user_session.get("runnable")  # type: Runnable

    msg = cl.Message(content="")

    async for chunk in runnable.astream(
        {"question": message.content},
        config=RunnableConfig(callbacks=[cl.LangchainCallbackHandler()]),
    ):
        await msg.stream_token(chunk)

    await msg.send()
