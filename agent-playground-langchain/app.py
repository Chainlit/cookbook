
import os
from chainlit.playground.config import add_llm_provider
from chainlit.playground.providers.langchain import LangchainGenericProvider
from langchain.llms import HuggingFaceHub
from langchain import PromptTemplate, LLMChain
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
        is_chat=False
    )
)



template = """Question: {question}

Answer:"""

prompt = PromptTemplate(template=template, input_variables=["question"])

llm_chain = LLMChain(prompt=prompt, llm=llm)


@cl.on_message
async def main(message: str):
    response = await llm_chain.arun(message, callbacks=[cl.AsyncLangchainCallbackHandler()])

