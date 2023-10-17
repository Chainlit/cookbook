import json

from langchain.agents import AgentExecutor

from chainlit.langflow import load_flow
import chainlit as cl


with open("./schema.json", "r") as f:
    schema = json.load(f)


@cl.on_chat_start
async def start():
    flow = await load_flow(schema=schema)
    cl.user_session.set("flow", flow)


@cl.on_message
async def main(message: cl.Message):
    # Load the flow from the user session
    flow = cl.user_session.get("flow")  # type: AgentExecutor

    # Enable streaming
    flow.agent.llm_chain.llm.streaming = True

    # Run the flow
    res = await cl.make_async(flow.run)(
        message.content, callbacks=[cl.LangchainCallbackHandler()]
    )

    # Send the response
    await cl.Message(content=res).send()
