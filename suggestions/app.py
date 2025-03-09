import chainlit as cl


@cl.on_message
async def on_message(msg: cl.Message):
    suggestions = cl.CustomElement(name="FollowUpSuggestions", suggestions=["Foo", "Bar"])
    await cl.Message(content="Suggestions:", elements=[suggestions]).send()