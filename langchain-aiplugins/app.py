from langchain.chat_models import ChatOpenAI
from langchain.agents import load_tools, initialize_agent, AgentExecutor
from langchain.agents import AgentType
from langchain.tools import AIPluginTool
import chainlit as cl


@cl.on_chat_start
def start():
    tool = AIPluginTool.from_plugin_url(
        "https://www.klarna.com/.well-known/ai-plugin.json"
    )
    llm = ChatOpenAI(temperature=0, streaming=True)
    tools = load_tools(["requests_all"])
    tools += [tool]

    agent = initialize_agent(
        tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True
    )

    cl.user_session.set("agent", agent)


@cl.on_message
async def main(message: cl.Message):
    agent = cl.user_session.get("agent")  # type: AgentExecutor
    res = await agent.arun(
        message.content, callbacks=[cl.AsyncLangchainCallbackHandler()]
    )

    await cl.Message(content=res).send()
