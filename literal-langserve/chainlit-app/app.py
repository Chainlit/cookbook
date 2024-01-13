from langserve import RemoteRunnable

import chainlit as cl


@cl.step(type="run")
async def invoke_runnable(input: str):
    test_chain = RemoteRunnable(
        "http://localhost:8001/test/",
        headers={
            "thread_id": cl.context.session.thread_id,
            "run_id": cl.context.current_step.id,
        },
    )

    return await test_chain.ainvoke(input)


@cl.on_message
async def on_msg(msg: cl.Message):
    response = await invoke_runnable(msg.content)
    await cl.Message(content=f"Retrieved {len(response)} documents!").send()
