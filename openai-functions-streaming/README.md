Title: OpenAI functions streaming with Chainlit
Tags: [openai-functions]

# OpenAI Functions Streaming with Chainlit

This directory contains an example of how to integrate OpenAI's powerful language model with Chainlit to create an interactive chat application that can call custom functions defined in your code. The example demonstrates a simple function that fetches the current weather for a specified location.

## Quickstart

To get started with this example, follow these steps:

1. Ensure you have Python installed on your system.
2. Clone the repository and navigate to this directory.
3. Install the required dependencies by running `pip install -r requirements.txt`.
4. Set your OpenAI API key as an environment variable: `export OPENAI_API_KEY='your_api_key'`.
5. Run the application with `python app.py`.

### Function Definition

The core functionality is provided by the `get_current_weather` function defined in `app.py`. This function takes a `location` and a `unit` (Celsius or Fahrenheit) as arguments and returns a JSON string with the weather information.    
```python
def get_current_weather(location, unit):
unit = unit or "Fahrenheit"
weather_info = {
"location": location,
"temperature": "60", # Placeholder value
"unit": unit,
"forecast": ["windy"], # Placeholder forecast
}
return json.dumps(weather_info)
```

### Using the Function with Chainlit

The `call_tool` async function in `app.py` is designed to handle the invocation of `get_current_weather` from the chat interface. It processes the arguments, calls the function, and appends the result to the message history.

### Interacting with the Chatbot

Once the application is running, you can interact with the chatbot through the Chainlit interface. The chatbot will use the OpenAI model to understand your requests and, when necessary, call the `get_current_weather` function to provide you with the weather information.

![Rendering](./streaming-functions.gif)

For detailed instructions and more information, refer to the [main readme](/README.md).

OpenAI functions enable GPT to use functions you defined in your code.
To run the example, follow the instructions of the [main readme](/README.md).

![Rendering](./streaming-functions.gif)
