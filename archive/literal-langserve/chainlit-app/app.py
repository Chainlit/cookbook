from langserve import RemoteRunnable

import chainlit as cl


def get_runnable():
    runnable = RemoteRunnable(
        "http://localhost:8001/test/",
        headers={
            "thread_id": cl.context.session.thread_id,
        },
    )

    return runnable


@cl.on_message
async def on_msg(msg: cl.Message):
    msg = cl.Message(content="")

    async for chunk in get_runnable().astream(
        {"question": msg.content},
    ):
        await msg.stream_token(chunk)

    await msg.send()
