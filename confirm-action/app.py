import chainlit as cl


@cl.on_chat_start
async def main():
    res = await cl.AskActionMessage(
        content="Pick an action!",
        actions=[
            cl.Action(name="continue", payload={"value": "continue"}, label="✅ Continue"),
            cl.Action(name="cancel", payload={"value": "cancel"}, label="❌ Cancel"),
        ],
    ).send()

    if res and res.get.get("payload").get("value") == "continue":
        await cl.Message(
            content="Continue!",
        ).send()
