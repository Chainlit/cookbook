from langchain import OpenAI, LLMMathChain, SerpAPIWrapper
from langchain.agents import initialize_agent, Tool
from langchain.chat_models import ChatOpenAI
import os
from typing import *
from langchain.tools import BaseTool

import chainlit as cl
from chainlit.sync import run_sync


class HumanInputChainlit(BaseTool):
    """Tool that adds the capability to ask user for input."""

    name = "human"
    description = (
           "You can ask a human for guidance when you think you "
            "got stuck or you are not sure what to do next. "
            "The input should be a question for the human."
           )

    def _run(
            self,
            query: str,
            run_manager=None,
        ) -> str:
        """Use the Human input tool."""

        res = run_sync(cl.AskUserMessage(content=query).send())
        return res['content']

    async def _arun(
        self,
        query: str,
        run_manager=None,
    ) -> str:
        """Use the Human input tool."""
        res = await cl.AskUserMessage(content=query).send()
        return res['content']


# Could you async but make sure all tools have an async implem
@cl.langchain_factory(use_async=False)
async def load():
    llm = ChatOpenAI(temperature=0, streaming=True)
    llm1 = OpenAI(temperature=0, streaming=True)
    llm_math_chain = LLMMathChain.from_llm(llm=llm, verbose=True)

    # fyi, the calculator tool only has a sync implementation
    tools = [
        HumanInputChainlit(),
        Tool(
            name="Calculator",
            func=llm_math_chain.run,
            description="useful for when you need to answer questions about math",
        ),
    ]
    return initialize_agent(
        tools, llm1, agent="chat-zero-shot-react-description", verbose=True
    )
