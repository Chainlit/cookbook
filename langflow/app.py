import json

from langchain.agents import AgentExecutor

import chainlit as cl


with open("./schema.json", "r") as f:
    schema = json.load(f)


@cl.langflow_factory(
    schema=schema,  # dict or the api url to your langflow schema
    tweaks={},  # optional Langflow tweaks dict
    use_async=False,
)
def factory(agent: AgentExecutor):
    # Modify your agent here if needed
    agent.agent.llm_chain.llm.streaming = True
    return agent
