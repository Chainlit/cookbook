# LangGraph README

LangGraph is a conversational AI framework designed to facilitate the creation of complex conversational workflows. It leverages the power of LangChain, a modular AI framework, to enable the integration of various AI tools and models into a single, cohesive system.

## Key Features

* Modular architecture allowing for easy integration of new AI tools and models
* Support for conditional workflows based on user input and AI model outputs
* Real-time conversation handling with streaming capabilities
* Integration with Tavily for vector search and document retrieval
* Support for multiple AI models, including OpenAI and Tavily

## Getting Started

To get started with LangGraph, follow these steps:

1. Install the required dependencies by running `pip install -r requirements.txt`
2. Set up your environment variables by creating a `.env` file with the necessary API keys and configuration
3. Run the application using `chainlit run app.py`
4. Interact with the system by sending messages to the chat interface (ask about the weather in San Francisco, for example)

## Configuration

LangGraph relies on environment variables for configuration. The following variables are required:

* `OPENAI_API_KEY`: Your OpenAI API key
* `TAVILY_API_KEY`: Your Tavily API key

## Contributing

Contributions to LangGraph are welcome. If you'd like to contribute, please follow these steps:

1. Fork the repository
2. Make your changes
3. Submit a pull request

## License

LangGraph is licensed under the MIT License.
