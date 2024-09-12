# Assistant Management System

This project is an Assistant Management System built using Python and the Chainlit library. It allows users to create, manage, and interact with virtual assistants. The assistants are configured with various settings and can respond to user messages based on predefined instructions.

## Features

- Create and manage virtual assistants.
- Customize assistant settings including name, description, icon, instructions, model, and temperature.
- Store assistants in a list (for demo purposes; a database is recommended for production).
- Authenticate users with a simple username and password.
- Interact with assistants through a chat interface.

## Setup

### Prerequisites

- Python 3.7 or higher
- Chainlit library
- Mistral AI client and an API key (you can get it [here](https://console.mistral.ai/))

### Installation

1. Install the required dependencies:
```sh
pip install -r requirements.txt
```

2. Run the application:
```sh
python app.py
```

## Code Overview

### Main Components

- **Assistant Settings**: Defined using various input widgets like `TextInput`, `FileUploadInput`, `Select`, and `Slider` to customize the assistant's properties.
- **Default Assistant**: A default assistant is created with predefined settings and added to the `ASSISTANTSLIST`.
- **Callbacks**: Various Chainlit callbacks are used to handle chat start, assistant creation, listing assistants, and message handling.

## Usage

1. Start the application with `chainlit run app.py`.
2. Authenticate using the username `admin` and password `admin`.
3. Create or select an assistant, and add instructions to aply when answering to the user.
4. Interact with the assistant by sending messages.

## Notes

- This project is for demonstration purposes. For production use, consider storing assistants in a database and implementing a more secure authentication mechanism.
- The Mistral AI client is used as LLM API, you need to have an account and an API key to use it. You can change the API key in the `app.py` file, or use any other LLM API.

## Migration from ChatProfiles to AssistantProfiles

### Update the code

Remove the decorator `@cl.set_chat_profiles` and set the `AssistantSettings` in the `@cl.on_chat_start` decorator.

You can define assistant settings using the Assistant class:

```python
@cl.on_chat_start
async def on_chat_start():
    await cl.AssistantSettings(assistant_settings).send()
```

These settings are used to configure the assistant, and are sent to the frontend. The fields should be a list of `InputWidget` that you can find in `chainlit.input_widget`.

Finally, you need to write the functions for the two decorators `@cl.on_create_assistant` and `@cl.on_list_assistants`, which are used respectively to create a new assistant and to list all the assistants in the project.

Example:
```python
@cl.on_list_assistants
async def list_assistants(user):
    return ASSISTANTSLIST
```

### Update API calls:

Replace any API calls using ChatProfiles with the new Assistant-based calls (in the given code, the function `run_assistant` is used to run the assistant, and it uses the `selected_assistant` variable to get the assistant settings).

### UI updates:

The UI is automatically updated to use the new Assistant system, you don't need to do anything.

Note: Be careful to use the Chat Profiles OR the Assistant Profiles, don't use both at the same time, or you will have conflicts.
