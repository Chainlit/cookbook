import chainlit as cl
from chainlit.action import Action

from tools import generate_image_tool, edit_image_tool
from langchain.agents import initialize_agent, AgentType
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.agents.structured_chat.prompt import SUFFIX


@cl.action_callback("Create variation")
async def create_variant(action: Action):
    agent = cl.user_session.get("agent")
    agent_input = f"Create a variation of {action.value}"
    await cl.Message(content=f"Creating a variation of `{action.value}`.").send()
    await run(agent, agent_input)


@cl.langchain_rename
def rename(orig_author):
    mapping = {
        "LLMChain": "Assistant",
    }
    return mapping.get(orig_author, orig_author)


@cl.langchain_factory(use_async=False)
def main():
    llm = ChatOpenAI(temperature=0, streaming=True)
    tools = [generate_image_tool, edit_image_tool]
    memory = ConversationBufferMemory(memory_key="chat_history")
    _SUFFIX = "Chat history:\n{chat_history}\n\n" + SUFFIX

    agent_executor = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
        memory=memory,
        agent_kwargs={
            "suffix": _SUFFIX,
            "input_variables": ["input", "agent_scratchpad", "chat_history"],
        },
    )

    return agent_executor


@cl.langchain_run
async def run(agent_executor, action_input):
    cl.user_session.set("generated_image", None)

    # No async implementation in the Stability AI client, fallback to sync
    res = await cl.make_async(agent_executor.run)(
        input=action_input, callbacks=[cl.LangchainCallbackHandler()]
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
