import uuid
import chainlit as cl
from mistralai.async_client import MistralAsyncClient
from typing import List
from chainlit.input_widget import Select, TextInput, FileUploadInput, Slider
from chainlit.assistant import Assistant
import logging

logging.basicConfig(level=logging.INFO)

# Definitely not the best way to store assistants (use a database instead)
ASSISTANTSLIST : List[Assistant] = []

# Instrument the Mistral AI client
cl.instrument_mistralai()

assistant_settings = [
    TextInput(
        id="name",
        label="Name",
        placeholder="Name of the assistant",
    ),
    TextInput(
        id="markdown_description",
        label="Description",
        placeholder="Description of the assistant",
        multiline=True,
    ),
    FileUploadInput(
        id="icon",
        label="Icon",
        accept=["image/*"],
        max_size_mb=5,
        max_files=1,
        placeholder="Icon for the assistant",
    ),
    TextInput(
        id="instructions",
        label="Instructions",
        placeholder="Instructions for the assistant",
        multiline=True,
    ),
    Select(
        id="model",
        label="Model",
        values=["mistral-large-latest"],
        initial_value="gpt-4o"
    ),
    Slider(
        id="temperature",
        label="Temperature",
        min=0,
        max=1,
        step=0.1,
        initial=0.5,
    ),
]

# create a default assistant
default_assistant = Assistant(
    settings_values={
        "name": "Georges",
        "markdown_description": "Georges is a dumb assistant",
        "icon": "https://picsum.photos/250",
        "instructions": "Only answer \"Georges\" to every question you are asked.",
        "model": "gpt-4o",
        "temperature": 0.5,
        "created_by": "toto",
        "id": str(uuid.uuid4())
    },
    input_widgets=assistant_settings
)

ASSISTANTSLIST.append(default_assistant)

# send the assistant settings to the backend (to be used in the frontend)
@cl.on_chat_start
async def on_chat_start():
    # await cl.AssistantSettings(assistant_settings).send()
    await cl.AssistantSettings(assistant_settings).send()

# callback to create an assistant
@cl.on_create_assistant
async def create_assistant(user, new_assistant: Assistant):
    # if an assistant with the same name already exists, update it
    if any(assistant.settings_values['name'] == new_assistant.settings_values['name'] for assistant in ASSISTANTSLIST):
        for assistant in ASSISTANTSLIST:
            if assistant.settings_values['name'] == new_assistant.settings_values['name']:
                assistant.settings_values = new_assistant.settings_values
                assistant.input_widgets = new_assistant.input_widgets
                break
    else:
        ASSISTANTSLIST.append(new_assistant)
        
# return the list of assistants
@cl.on_list_assistants
async def list_assistants(user):
    return ASSISTANTSLIST

mai_client = MistralAsyncClient()

async def run_assistant(assistant: dict, message: cl.Message):
    response = await mai_client.chat(
        messages=[
            {
                "content": assistant.settings_values["instructions"] if assistant.settings_values["instructions"] else "You are a helpful assistant",
                "role": "system"
            },
            {
                "content": message.content,
                "role": "user"
            }
        ],
        model=assistant.settings_values["model"] if assistant.settings_values["model"] else "mistral-large-latest",
        temperature=assistant.settings_values["temperature"] if assistant.settings_values["temperature"] else 0.5
    )
    return response.choices[0].message.content


@cl.password_auth_callback
def auth_callback(username: str, password: str):
    # do not use this in production, it's just for demo purposes
    if (username, password) == ("admin", "admin"):
        return cl.User(
            identifier="admin", metadata={"role": "ADMIN", "provider": "credentials"}
        )
    else:
        return None

@cl.on_message
async def main(message: cl.Message):
    selected_assistant = cl.user_session.get("selected_assistant")
    if selected_assistant:
        await cl.Message(content=await run_assistant(selected_assistant, message)).send()
    else:
        await cl.Message(content="No assistant selected").send()
