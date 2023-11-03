##########################################################################
#
#
# Waiting on https://github.com/microsoft/autogen/issues/527 to be solved
#
#
##########################################################################


from typing import Dict, Optional, Union

from autogen import Agent, AssistantAgent, UserProxyAgent, config_list_from_json
import chainlit as cl

TASK = "Plot a chart of NVDA stock price change YTD and save it on disk."


async def ask_helper(func, **kwargs):
    res = await func(**kwargs).send()
    while not res:
        res = await func(**kwargs).send()
    return res


class ChainlitAssistantAgent(AssistantAgent):
    async def a_send(
        self,
        message: Union[Dict, str],
        recipient: Agent,
        request_reply: Optional[bool] = None,
        silent: Optional[bool] = False,
    ) -> bool:
        await cl.Message(
            content=f'*Sending message to "{recipient.name}":*\n\n{message}',
            author="AssistantAgent",
        ).send()
        await super(ChainlitAssistantAgent, self).a_send(
            message=message,
            recipient=recipient,
            request_reply=request_reply,
            silent=silent,
        )


class ChainlitUserProxyAgent(UserProxyAgent):
    async def get_human_input(self, prompt: str) -> str:
        if prompt.startswith(
            "Provide feedback to assistant. Press enter to skip and use auto-reply"
        ):
            res = await ask_helper(
                cl.AskActionMessage,
                content="Continue or provide feedback?",
                actions=[
                        cl.Action(
                            name="continue", value="continue", label="✅ Continue"
                        ),
                    cl.Action(
                            name="feedback",
                            value="feedback",
                            label="💬 Provide feedback",
                        ),
                    cl.Action(
                            name="exit",
                            value="exit",
                            label="🔚 Exit Conversation"
                        ),
                ],
            )
            if res.get("value") == "continue":
                return ""
            if res.get("value") == "exit":
                return "exit"

        reply = await ask_helper(
            cl.AskUserMessage, content=prompt, timeout=60)

        return reply["content"].strip()

    async def a_send(
        self,
        message: Union[Dict, str],
        recipient: Agent,
        request_reply: Optional[bool] = None,
        silent: Optional[bool] = False,
    ):
        await cl.Message(
            content=f'*Sending message to "{recipient.name}"*:\n\n{message}',
            author="UserProxyAgent",
        ).send()
        await super(ChainlitUserProxyAgent, self).a_send(
            message=message,
            recipient=recipient,
            request_reply=request_reply,
            silent=silent,
        )


@cl.on_chat_start
async def on_chat_start():
    config_list = config_list_from_json(env_or_file="OAI_CONFIG_LIST")
    assistant = ChainlitAssistantAgent(
        "assistant", llm_config={"config_list": config_list}
    )
    user_proxy = ChainlitUserProxyAgent(
        "user_proxy",
        code_execution_config={
            "work_dir": "workspace",
            "use_docker": False,
        },
    )
    await cl.Message(content=f"Starting agents on task: {TASK}...").send()
    await user_proxy.a_initiate_chat(
        assistant,
        message=TASK,
    )
