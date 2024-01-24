---
title: 'Baseten Llama 2 Chat Interface'
tags: ['baseten', 'llama2']
---

# Baseten Llama 2 Chat Interface

This repository contains a Chainlit application that provides a chat interface for interacting with the Llama 2 model hosted on Baseten. It simulates a ChatGPT-like experience, allowing users to have context-aware conversations with the AI model.

## High-Level Description

The `app.py` script sets up a Chainlit application that listens for user messages. When a message is received, it constructs a prompt from the user's message history and sends a request to the Llama 2 model deployed on Baseten. The response from the model is streamed back to the user, providing an interactive chat experience. The application maintains the context of the conversation by storing the prompt history in the user's session.

## Quickstart

### Prerequisites

- Python 3.9 or higher
- Baseten account with an API key
- Deployed Llama 2 model on Baseten

### Setup and Run

1. **Install Dependencies:**

Install the required libraries using pip.

```shell
pip install --upgrade baseten chainlit
```

2. **Environment Configuration:**

Set the necessary environment variables in your `.env` file. Find the example .env called '.env.example' in this repository.

```shell
cp .env.example .env
```
Set your env values in the .env file.
BASETEN_API_KEY=your_baseten_api_key
VERSION_ID=your_deployed_model_version_id

3. **Run the Application:**

Start the Chainlit application with the following command:

```shell
chainlit run app.py -w
```


## Code Overview

- `main()`: An asynchronous function that handles incoming messages, constructs prompts, and sends requests to the Llama 2 model.
- `version_id`: The version ID of the deployed Llama 2 model on Baseten.
- `baseten_api_key`: The API key for authenticating requests to Baseten.

The application uses the `requests` library to send POST requests to the Baseten model endpoint, streaming the response back to the user in real-time.

## Credits

This application is designed to work with the Llama 2 model available on Baseten. For more information on deploying models on Baseten, visit their [official documentation](https://docs.baseten.co/).

