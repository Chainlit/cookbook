import os
import chainlit as cl
import asyncio
from openai import AsyncAssistantEventHandler


from openai import AsyncOpenAI

client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


class EventHandler(AsyncAssistantEventHandler):

    def __init__(self) -> None:
        super().__init__()
        self.current_message = None
        self.current_tool_call = None

    async def on_text_created(self, text) -> None:
        print("------", text)
        print(f"\nassistant > ", end="", flush=True)
        self.current_message = cl.Message(content="")

    async def on_text_delta(self, delta, snapshot):
        print(delta.value, end="", flush=True)
        await self.current_message.stream_token(delta.value)

    async def on_text_done(self, text):
        await self.current_message.send()

    async def on_tool_call_created(self, tool_call):
        print(tool_call.__dict__)
        print(f"\nassistant > {tool_call.type}\n", flush=True)
        self.current_message = cl.Message(author=f"{tool_call.type}", content="", language="python")
        await self.current_message.send()

    async def on_tool_call_delta(self, delta, snapshot):
        if snapshot.id != self.current_tool_call:
            self.current_tool_call = snapshot.id
            self.current_message = cl.Message(author=f"{delta.type}", content="", language="python")
            await self.current_message.send()

        if delta.type == 'code_interpreter':
            if delta.code_interpreter.input:
                print(delta.code_interpreter.input, end="", flush=True)
                await self.current_message.stream_token(delta.code_interpreter.input)
            if delta.code_interpreter.outputs:
                print(f"\n\noutput >", flush=True)
                for output in delta.code_interpreter.outputs:
                    if output.type == "logs":
                        print(f"\n{output.logs}", flush=True)
                        await cl.Message(author=f"{delta.type}", content=output.logs, language="markdown").send()

    async def on_tool_call_done(self, text):
        await self.current_message.send()
    

@cl.on_chat_start
async def start_chat():
    # Create an Assistant
    assistant = await client.beta.assistants.retrieve("asst_DRr99sEtdRgjJZoHpjDjrOU8")

    # Store assistant ID in user session for later use
    cl.user_session.set("assistant_id", assistant.id)

    # Create a Thread
    thread = await client.beta.threads.create()
    # Store thread ID in user session for later use
    cl.user_session.set("thread_id", thread.id)


@cl.on_message
async def main(message: cl.Message):
    assistant_id = cl.user_session.get("assistant_id")
    thread_id = cl.user_session.get("thread_id")

    # Add a Message to the Thread
    oai_message = await client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=message.content
    )

    # Create and Stream a Run
    async with client.beta.threads.runs.stream(
        thread_id=thread_id,
        assistant_id=assistant_id,
        instructions="Please assist the user with their query.",
        event_handler=EventHandler(),
    ) as stream:
        await stream.until_done()
