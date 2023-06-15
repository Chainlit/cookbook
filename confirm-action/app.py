import chainlit as cl

# This is a simple example on how to prompt a user to confirm or reject an action.


@cl.action_callback("confirm_action")
async def on_action(action: cl.Action):
    if action.value == "ok":
        content = "Confirmed!"
    elif action.value == "not_ok":
        content = "Rejected!"
    else:
        await cl.ErrorMessage(content="Invalid action").send()
        return

    actions = cl.user_session.get("actions")
    if actions:
        for action in actions:
            await action.remove()
        cl.user_session.set("actions", None)

    await cl.Message(content=content).send()


@cl.on_chat_start
async def start():
    approve_action = cl.Action(name="confirm_action", value="ok", label="Confirm")
    reject_action = cl.Action(name="confirm_action", value="not_ok", label="Reject")
    actions = [approve_action, reject_action]
    cl.user_session.set("actions", actions)

    await cl.Message(
        content="Test message",
        actions=actions,
    ).send()
