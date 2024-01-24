Title: Multimodal chat 
Tags: [multimodal]

# LLaVa with Chainlit

![LLaVa Chainlit Example](https://github.com/Chainlit/cookbook/assets/13104895/01904f09-b1f2-4755-ae42-5a4276bd46e1)

LLaVa (Language Llama) is a multimodal conversational AI that can understand and generate text and images. This Chainlit example demonstrates how to integrate LLaVa into a Chainlit application, allowing users to interact with the AI through a chat interface that supports both text and image inputs.

## Key Features

- **Multimodal Interaction**: Users can converse with the AI using text and images.
- **Customizable Conversation Styles**: Different separator styles for conversation formatting.
- **Image Processing**: Supports various image processing modes like padding, cropping, and resizing.
- **Asynchronous Request Handling**: Communicates with the LLaVa backend asynchronously for efficient performance.

## Quickstart

1. **Set up LLaVa**: Deploy LLaVa and obtain a `CONTROLLER_URL` by following the instructions in this [YouTube video](https://www.youtube.com/watch?v=kx1VpI6JzsY).
2. **Environment Variable**: Ensure the `CONTROLLER_URL` is set in your environment variables.
3. **Install Dependencies**: Install the required Python packages including `chainlit`, `aiohttp`, and `PIL`.
4. **Run the App**: Start the Chainlit app by running `app.py`.

## Function Definitions

- `Conversation`: A dataclass that keeps all conversation history, including system messages, roles, and separator styles.
- `request`: An asynchronous function that sends the user's input to the LLaVa backend and streams the response back to the user.
- `start`: An event handler that initializes the chat settings when a new chat session starts.
- `setup_agent`: Updates the chat settings when the user changes them.
- `main`: The main event handler for incoming messages. It processes images, appends messages to the conversation, and sends requests to the LLaVa backend.

LLaVa (Language Llama) is a multimodal conversational AI that can understand and generate text and images. This Chainlit example demonstrates how to integrate LLaVa into a Chainlit application, allowing users to interact with the AI through a chat interface that supports both text and image inputs.

## Key Features

- **Multimodal Interaction**: Users can converse with the AI using text and images.
- **Customizable Conversation Styles**: Different separator styles for conversation formatting.
- **Image Processing**: Supports various image processing modes like padding, cropping, and resizing.
- **Asynchronous Request Handling**: Communicates with the LLaVa backend asynchronously for efficient performance.

## Quickstart

1. **Set up LLaVa**: Deploy LLaVa and obtain a `CONTROLLER_URL` by following the instructions in this [YouTube video](https://www.youtube.com/watch?v=kx1VpI6JzsY).
2. **Environment Variable**: Ensure the `CONTROLLER_URL` is set in your environment variables.
3. **Install Dependencies**: Install the required Python packages including `chainlit`, `aiohttp`, and `PIL`.
4. **Run the App**: Start the Chainlit app by running `app.py`.

## Function Definitions

- `Conversation`: A dataclass that keeps all conversation history, including system messages, roles, and separator styles.
- `request`: An asynchronous function that sends the user's input to the LLaVa backend and streams the response back to the user.
- `start`: An event handler that initializes the chat settings when a new chat session starts.
- `setup_agent`: Updates the chat settings when the user changes them.
- `main`: The main event handler for incoming messages. It processes images, appends messages to the conversation, and sends requests to the LLaVa backend.

## Credits

Full credits to the LLaVa team ([GitHub repo](https://github.com/haotian-liu/LLaVA/)). This example is heavily inspired by the original logic written for the Gradio app. The goal of this example is to provide the community with a working example of LLaVa with Chainlit.

## How to deploy LLaVa





