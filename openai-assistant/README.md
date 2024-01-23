Title: OpenAI Assistant API with Chainlit
Tags: [openai, assistant-api]

# OpenAI Assistant API with Chainlit

![OpenAI Assistant](https://github.com/Chainlit/cookbook/assets/13104895/8a56c03f-ca04-4d64-b8a7-72498b4e274f)

This repository contains code for integrating OpenAI's Assistant API with Chainlit to create a versatile assistant capable of handling math queries and providing weather updates.

## Features

- **Math Tutor**: Solve math problems by writing and running code. Math expressions are displayed using LaTeX for clarity.
- **Weather Bot**: Get current weather and N-day forecasts based on user location and preferred temperature unit.
- **Interactive UI**: Chainlit provides an interactive user interface for inputting queries and displaying responses.

## Quickstart

To get started with the OpenAI Assistant API with Chainlit, follow these steps:

1. Clone the repository and navigate to the `openai-assistant` directory.
2. Install the required dependencies using `pip install -r requirements.txt`.
3. Set up your environment variables by creating a `.env` file with your `OPENAI_API_KEY` and `ASSISTANT_ID`.
4. Run the `create_assistant.py` script to create an assistant instance.
5. Start the Chainlit app by running `app.py`.

### Example Usage


Note: Streaming is not supported yet.
