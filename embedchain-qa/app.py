import os

import chainlit as cl

from embedchain import App

os.environ["OPENAI_API_KEY"] = "OPENAI_API_KEY"


@cl.on_chat_start
async def on_chat_start():
    app = App.from_config(
        config={
            "app": {"config": {"name": "chainlit-app"}},
            "llm": {
                "config": {
                    "stream": True,
                    "model": "gpt-3.5-turbo-16k",
                    "temperature": 0.5,
                    "max_tokens": 4000,
                }
            },
        }
    )
    # import your data here
    app.add("https://docs.chainlit.io/",data_type="docs_site")
    app.collect_metrics = True
    cl.user_session.set("app", app)


@cl.on_message
async def on_message(message: cl.Message):
    app = cl.user_session.get("app")
    msg = cl.Message(content="")
    for chunk in await cl.make_async(app.chat)(message.content):
        await msg.stream_token(chunk)

    await msg.send()