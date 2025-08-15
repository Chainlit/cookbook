# Chainlit application with ReAct agent

This repository contains a chainlit application powered by a LangGraph ReAct agent. The two main challenges for creating an LLM chat app are the python sandbox code execution and performant document loading. There may be better solutions for these in the future.

## Features

- **AI Agent Integration**: Supports AI tools for Retrieval-augmented generation (RAG), web search, and file upload.
- **Azure AI Integration**: Utilizes Azure AI Document Intelligence as well as local parsers for file processing.
- **Dynamic Context Handling**: Dynamically adjusts context based on user input and uploaded files.

## Supported File Types

The application supports the following file types for upload and processing:

- `.pdf`
- `.docx`
- `.xlsx`
- `.pptx`
- `.txt`
- `.jpeg`
- `.png`
- `.bmp`
- `.tiff`
- `.heif`
- `.html`

These types are handled differently for performance reasons. While Document Intelligence can also handle text types (parsing the layout as well!), it does so with a large hit to performance. Similarly, Unstructured is an alternative parser for PDF and other file types, but it is approximately twice as slow for large PDFs and results in a very large Docker image (15 GB+), which can be challenging to host. The main challenge for document parsing is not open source code, but compute (GPU resources to parse documents).

The approach taken here is similar to Open WebUI and AnythingLLM, using different parsers for different file formats.

# Python code sandbox

The langchain_sandbox library is used here, since it doesn't require hosting of any additional resources.

## Folder Structure

- `tools`: Contains tools for RAG search and uploaded file search.
- `services`: Includes Azure integration services.
- `app.py`: Main application file.

## Usage

1. Create a virtual environment using: python -m venv .venv
2. Use the virtual environment using: .venv\Scripts\activate
3. Install the dependencies using pip install -r requirements.txt
4. Install deno: https://docs.deno.com/runtime/getting_started/installation/
5. Run the app from the virtual environment, using: chainlit run app.py

## Extending the Application

To add new tools or functionalities:

1. Define new tools in the `tools` folder.
2. Update the agent creation logic in `setup_runnable`.

## Contributing

Contributions are welcome! Please follow the standard GitHub flow for submitting pull requests.