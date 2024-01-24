---
title: 'Chat your Pinecone database'
tags: ['pinecone', 'chainlit']
---

# Chat your Pinecone database

This folder contains an example application that demonstrates how to:
- Connect to a pre-populated Pinecone database.
- Answer user queries using the data stored in the Pinecone database, and provide the sources for the answers.

## High-Level Description

The application uses the `langchain` library to create a conversational AI that interacts with users. It leverages Pinecone's vector database to retrieve relevant documents that answer user queries. The `ConversationalRetrievalChain` class from `langchain` is used to build the AI chain that processes the user's input, searches the Pinecone database, and returns an answer along with the sources.

## Quickstart

To run the example, ensure you have populated a Pinecone database and have the necessary API keys. Follow these steps:

1. Install the required dependencies by running `pip install -r requirements.txt` in your terminal.
2. Set your Pinecone API key and environment as environment variables: 
`export PINECONE_API_KEY='your_api_key'` and `export PINECONE_ENV='your_environment'`.
3. Run the application with `chainlit run app.py`.

### Key Functions

- `start()`: Initializes the chat session, sends a welcome message, and sets up the conversational chain with Pinecone as the retriever.
- `main(message: cl.Message)`: Handles incoming messages, processes them through the conversational chain, and sends back the answer with source references.

### Code Definitions

- `Pinecone.from_existing_index()`: Connects to an existing Pinecone index.
- `ConversationalRetrievalChain.from_llm()`: Creates a conversational chain with a language model and a document retriever.
- `cl.on_chat_start`: Decorator to initialize chat session.
- `cl.on_message`: Decorator to handle incoming chat messages.

Remember to replace `index_name` with the name of your Pinecone index and `namespace` if you're using one.
