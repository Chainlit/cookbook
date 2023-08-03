# OSS ChatGPT

Welcome to a chat interface for open-source models like LLama 2.

This chat interface offers many familiar features from ChatGPT, including context-aware chats, chat history, streaming responses, and Markdown support.

## Model deployment

[Deploy Llama-2-chat 7B](https://app.baseten.co/explore/llama_2_7b_chat) from the Baseten model library.

Make sure to first follow the README instructions for getting access to the model on Hugging Face and setting your `hf_access_token` in your Baseten account.

## App setup

First, install the required libraries:

```
pip install --upgrade baseten chainlit
```

Then, set the required config in `env`. Use the Baseten UI to [create an API key](https://app.baseten.co/settings/account/api_keys) and find the version ID of your deployed model.

```sh
BASETEN_API_KEY=abcd.abcd1234
VERSION_ID=abcd123
```

## Run

```
chainlit run app.py -w
```