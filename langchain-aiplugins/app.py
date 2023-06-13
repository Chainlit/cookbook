from langchain.chat_models import ChatOpenAI
from langchain.agents import load_tools, initialize_agent
from langchain.agents import AgentType
from langchain.tools import AIPluginTool
from chainlit import langchain_factory


@langchain_factory(use_async=True)
def load():
    tool = AIPluginTool.from_plugin_url(
        "https://www.klarna.com/.well-known/ai-plugin.json"
    )
    llm = ChatOpenAI(temperature=0, streaming=True)
    tools = load_tools(["requests_all"])
    tools += [tool]

    return initialize_agent(
        tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True
    )
