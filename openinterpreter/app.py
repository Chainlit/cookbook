import interpreter
import chainlit as cl
from chainlit.input_widget import Select

import sys, os

interpreter.api_key = os.getenv("OPENAI_API_KEY")
# interpreter.debug_mode=True


# 1. Custom StdOut class to output prints to Chainlit UI
# 2. Custom StdIn class to receive input from Chainlit UI
# WARNING: Do not write prints in there, otherwise infinite loop
class CustomStdout:
    def __init__(self, original_stdout):
        self.original_stdout = original_stdout

    def write(self, data):
        # React to the data being written. For this example, I'm just printing to stderr.
        # language = ""
        # if interpreter.active_block and type(interpreter.active_block).__name__ == "CodeBlock":
        #     if interpreter.active_block.language:
        #         language = interpreter.active_block.language
        if data != "\n" and data != "":
            # cl.run_sync(cl.Message(content=data, language=language).send())
            cl.run_sync(cl.Message(content=data).send())
        # Write the data to the original stdout (so it still gets displayed)
        self.original_stdout.write(data)

    def flush(self):
        # If needed, you can also implement flush
        self.original_stdout.flush()


class CustomStdin:
    def __init__(self, original_stdin):
        self.original_stdin = original_stdin

    def readline(self):
        response_from_ui = cl.run_sync(cl.AskUserMessage(content="").send())
        return str(response_from_ui["content"])

    def flush(self):
        self.original_stdin.flush()


@cl.on_chat_start
async def start():
    sys.stdout = CustomStdout(sys.__stdout__)
    sys.stdin = CustomStdin(sys.__stdin__)
    settings = await cl.ChatSettings(
        [
            Select(
                id="model",
                label="OpenAI - Model",
                values=["gpt-3.5-turbo", "gpt-3.5-turbo-16k", "gpt-4", "gpt-4-32k"],
                initial_index=0,
            ),
        ]
    ).send()
    interpreter.model = settings["model"]


@cl.on_settings_update
async def setup_agent(settings):
    interpreter.model = settings["model"]
    await cl.Message(content=f"Chose OpenAI model {settings['model']}").send()


@cl.on_message
async def main(message: cl.Message):
    if message.elements:
        for element in message.elements:
            file_name = element.name
            content = element.content
            # If want to show content Content: {content.decode('utf-8')}\n\n
            await cl.Message(content=f"Uploaded file: {file_name}\n").send()

            # Save the file locally
            with open(file_name, "wb") as file:
                file.write(content)
            interpreter.load(
                [{"role": "assistant", "content": f"User uploaded file: {file_name}"}]
            )
    interpreter.chat(message.content)
