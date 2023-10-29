from typing import Dict, Optional, Union

from autogen import Agent, AssistantAgent, UserProxyAgent, config_list_from_json
import chainlit as cl

TASK = "Plot a chart of NVDA and FOO stock price change YTD and save it on disk."


class ChainlitUserProxyAgent(UserProxyAgent):
    def get_human_input(self, prompt: str) -> str:
        reply = cl.run_sync(cl.AskUserMessage(content=prompt, timeout=60).send())
        while not reply:
            reply = cl.run_sync(cl.AskUserMessage(content=prompt, timeout=60).send())
        return reply["content"].strip()

    def receive(
        self,
        message: Union[Dict, str],
        sender: Agent,
        request_reply: Optional[bool] = None,
        silent: Optional[bool] = False,
    ):
        print(f"Received message from {sender}")
        cl.run_sync(cl.Message(content=message).send())
        super(ChainlitUserProxyAgent, self).receive(
            message=message,
            sender=sender,
            request_reply=request_reply,
            silent=silent,
        )


@cl.on_chat_start
async def on_chat_start():
    config_list = config_list_from_json(env_or_file="OAI_CONFIG_LIST")
    assistant = AssistantAgent("assistant", llm_config={"config_list": config_list})

    user_proxy = ChainlitUserProxyAgent(
        "user_proxy",
        code_execution_config={
            "work_dir": "workspace",
            "use_docker": False,
        },
    )
    await cl.Message(content=f"Starting agents on task: {TASK}...").send()
    await cl.make_async(user_proxy.initiate_chat)(
        assistant,
        message=TASK,
    )
