import os

from langchain.llms import HuggingFaceHub
from langchain import PromptTemplate, LLMChain

import chainlit as cl
from chainlit.playground.config import add_llm_provider
from chainlit.playground.providers.langchain import LangchainGenericProvider

# You need to be approved by HF & Meta https://huggingface.co/meta-llama/Llama-2-7b-chat-hf/tree/main
# Large models like Llama2 also require a pro subscription

llm = HuggingFaceHub(
    model_kwargs={"max_length": 500},
    repo_id="meta-llama/Llama-2-7b-chat-hf",
    huggingfacehub_api_token=os.environ["HUGGINGFACEHUB_API_TOKEN"],
)


add_llm_provider(
    LangchainGenericProvider(
        id=llm._llm_type, name="HuggingFaceHub", llm=llm, is_chat=False
    )
)

template = """Question: {question}

Answer: Let's think step by step."""


@cl.on_chat_start
def main():
    # Instantiate the chain for that user session
    prompt = PromptTemplate(template=template, input_variables=["question"])
    llm_chain = LLMChain(prompt=prompt, llm=llm)

    # Store the chain in the user session
    cl.user_session.set("llm_chain", llm_chain)


@cl.on_message
async def main(message: cl.Message):
    # Retrieve the chain from the user session
    llm_chain = cl.user_session.get("llm_chain")  # type: LLMChain

    # Call the chain asynchronously
    res = await llm_chain.acall(
        message.content, callbacks=[cl.AsyncLangchainCallbackHandler()]
    )

    # Do any post processing here

    # "res" is a Dict. For this chain, we get the response by reading the "text" key.
    # This varies from chain to chain, you should check which key to read.
    await cl.Message(content=res["text"]).send()
