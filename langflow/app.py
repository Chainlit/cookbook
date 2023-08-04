import json

from langchain.agents import AgentExecutor

import chainlit as cl
from chainlit.langflow import load_flow
from chainlit.langchain.callbacks import LangchainCallbackHandler


with open("./schema.json", "r") as f:
    schema = json.load(f)


@cl.on_chat_start
async def start():
    flow = await load_flow(schema=schema)
    cl.user_session.set("flow", flow)


@cl.on_message
async def main(message):
    # Load the flow from the user session
    flow = cl.user_session.get("flow")  # type: AgentExecutor

    # Enable streaming
    flow.agent.llm_chain.llm.streaming = True

    # Run the flow
    res = await cl.make_async(flow.run)(
        message, callbacks=[LangchainCallbackHandler()]
    )

    # Send the response
    await cl.Message(content=res).send()
