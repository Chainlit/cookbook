from langchain.chains.llm_math.base import LLMMathChain
from langchain.agents import initialize_agent, Tool, AgentType, AgentExecutor
from langchain_openai import ChatOpenAI
from typing import *
from langchain.tools import BaseTool
from langchain_core.runnables import RunnableConfig
import chainlit as cl
from chainlit.sync import run_sync

from typing import Optional

from langchain_core.callbacks import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain_core.tools import BaseTool
from langchain_core.tools.base import ArgsSchema
from pydantic import BaseModel, Field
from langgraph.prebuilt import create_react_agent

class HumanInputSchema(BaseModel):
    query: str = Field(description="The question to ask the human")


class HumanInputChainlit(BaseTool):
    """Tool that adds the capability to ask user for input."""

    name: str = "human"
    description: str = (
        "You can ask a human for guidance when you think you "
        "got stuck or you are not sure what to do next. "
        "The input should be a question for the human."
    )
    args_schema: Optional[ArgsSchema] = HumanInputSchema
    return_direct: bool = False

    def _run(
        self,
        query: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Use the Human input tool."""
        res = run_sync(cl.AskUserMessage(content=query).send())
        return res["content"]
        return "test"

    async def _arun(
        self,
        query: str,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """Use the Human input tool."""
        res = await cl.AskUserMessage(content=query).send()
        return res["content"]
        # return "test"

@cl.on_chat_start
def start():
    llm = ChatOpenAI(temperature=0, streaming=True, model_name="gpt-4o")
    llm_math_chain = LLMMathChain.from_llm(llm=llm, verbose=True)

    tools = [
        HumanInputChainlit(),
        Tool(
            name="Calculator",
            func=llm_math_chain.invoke,
            description="useful for when you need to answer questions about math",
            coroutine=llm_math_chain.ainvoke,
        ),
    ]
    

    agent = create_react_agent(llm, tools=tools)

    cl.user_session.set("agent", agent)


@cl.on_message
async def main(message: cl.Message):
    agent = cl.user_session.get("agent")  # type: AgentExecutor
    config = RunnableConfig(callbacks=[cl.AsyncLangchainCallbackHandler()])
    inputs = {"messages": [("user", message.content)]}

    res = await agent.ainvoke(
        inputs, config=config
    )
    await cl.Message(content=res['messages'][-1].content).send()
