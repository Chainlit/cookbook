# Chat Application with ToolCallingAgent

This repository contains a Chat Application powered by AI models and tools for interacting with users, processing files, and retrieving relevant information.

## Features

- **AI Agent Integration**: Supports AI tools for RAG (Retrieve-then-Answer Generation) search, web search, and file search.
- **Azure AI Integration**: Utilizes Azure AI Document Intelligence for file processing.
- **Memory Management**: Includes conversation summary buffer memory for maintaining context.
- **File Upload Support**: Processes various file types like `.pdf`, `.xlsx`, `.docx`, `.pptx`, `.txt`, images, and more.
- **Custom Handlers**: Implements handlers for streaming AI responses and OAuth integration.
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

## Setup Instructions

Add the following configuration to `.chainlit/config.toml`:
```toml
cot = "tool_call"
```

## Folder Structure

- `tools`: Contains tools for RAG search, web search, and uploaded file search.
- `services`: Includes Azure integration services.
- `handlers`: Implements custom callback handlers for streaming and OAuth.
- `app.py`: Main application file.

## Usage

1. Start the chat application.
2. Upload files or send messages.
3. Interact with the AI-powered agent for information retrieval, summarization, and dynamic responses.

## Extending the Application

To add new tools or functionalities:

1. Define new tools in the `tools` folder.
2. Update the agent creation logic in `setup_runnable`.

## Contributing

Contributions are welcome! Please follow the standard GitHub flow for submitting pull requests.