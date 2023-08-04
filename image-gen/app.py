from tools import generate_image_tool, edit_image_tool
from langchain.agents import initialize_agent, AgentType, AgentExecutor
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.agents.structured_chat.prompt import SUFFIX

import chainlit as cl
from chainlit.action import Action
from chainlit.langchain.callbacks import LangchainCallbackHandler


@cl.action_callback("Create variation")
async def create_variant(action: Action):
    agent_input = f"Create a variation of {action.value}"
    await cl.Message(content=f"Creating a variation of `{action.value}`.").send()
    await main(agent_input)


@cl.author_rename
def rename(orig_author):
    mapping = {
        "LLMChain": "Assistant",
    }
    return mapping.get(orig_author, orig_author)


@cl.on_chat_start
def start():
    llm = ChatOpenAI(temperature=0, streaming=True)
    tools = [generate_image_tool, edit_image_tool]
    memory = ConversationBufferMemory(memory_key="chat_history")
    _SUFFIX = "Chat history:\n{chat_history}\n\n" + SUFFIX

    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
        memory=memory,
        agent_kwargs={
            "suffix": _SUFFIX,
            "input_variables": ["input", "agent_scratchpad", "chat_history"],
        },
    )
    cl.user_session.set("agent", agent)


@cl.on_message
async def main(message):
    agent = cl.user_session.get("agent")  # type: AgentExecutor
    cl.user_session.set("generated_image", None)

    # No async implementation in the Stability AI client, fallback to sync
    res = await cl.make_async(agent.run)(
        input=message, callbacks=[LangchainCallbackHandler()]
    )

    elements = []
    actions = []

    generated_image_name = cl.user_session.get("generated_image")
    generated_image = cl.user_session.get(generated_image_name)
    if generated_image:
        elements = [
            cl.Image(
                content=generated_image,
                name=generated_image_name,
                display="inline",
            )
        ]
        actions = [cl.Action(name="Create variation", value=generated_image_name)]

    await cl.Message(content=res, elements=elements, actions=actions).send()
