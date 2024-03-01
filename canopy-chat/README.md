---
title: 'Chat with Canopy'
tags: ['pinecone', 'chainlit', 'canopy']
---

# Chat your Canopy Server

This folder contains an example application that demonstrates how to:
- Connect to a running Canopy Server.
- Answer user queries using the data stored in the Pinecone database, and provide the sources for the answers.

## High-Level Description

The application uses the the Canopy-API Server. After you vectorised your index in Pinecone and have a running Canopy-Server you can start chatting with Pinecone RAG-Pipeline using OpenAI as LLM.

## Quickstart

To run the example, ensure you have a running Canopy-Server. Follow these steps:

1. Install the required dependencies by running `pip install -r requirements.txt` in your terminal.
2. Set your Canopy-API-URL into the `base_url`.
3. Run the application with `chainlit run app.py --port 8081`.