import chainlit as cl
from e2b_code_interpreter import CodeInterpreter
from agent import DataAgent

@cl.on_chat_start
async def on_start():
    cl.user_session.set("agent", DataAgent())
    

@cl.on_chat_end
async def on_start():
    agent = cl.user_session.get("agent")
    agent.close()

@cl.on_message
async def main(message: cl.Message):
    agent : DataAgent = cl.user_session.get("agent")

    await agent.run(message=message)

    await cl.Message(content=f"Received and uploaded {len(message.elements)} file(s) to the sandbox").send()

    # for format, data in r.raw.items():
    #     if format == "image/png":
    #         with open("image.png", "wb") as f:
    #             f.write(base64.b64decode(data))
    #         elements = [
    #             cl.Image(
    #                 url="image.png",
    #                 name="plot",
    #                 display="inline",
    #             )
    #         ]

    #         await cl.Message(content="plot", elements=elements).send()
    #     else:
    #         print(data)
    #         await cl.Message(content=data).send()

