# OpenAI Chat with Chainlit and Function Manager

Chainlit is an AI-powered project designed to perform a variety of tasks. It is built on a plugin architecture, allowing it to be easily extended with new functionalities.

## Project Features

- **Plugin Architecture**: Chainlit uses a flexible and extensible plugin architecture. Each plugin is a folder containing a `functions.py` and a `config.json` file, defining the functionality and configuration of the plugin.

- **Function Manager**: The Function Manager is responsible for parsing and invoking functions defined in the `functions.py` files of each plugin.

- **AI-Powered**: Chainlit leverages the power of AI to understand and generate human language, making it capable of handling a variety of tasks.

## Plugin Structure and Usage

Each plugin is a directory in the 'plugins' folder. The directory name is the plugin's name. Each plugin directory contains at least two files:

1. `functions.py`: This file contains the functions that the plugin provides. Each function should be a top-level function (i.e., not a method of a class or an inner function) and should be named in a way that reflects its functionality. Functions can be either synchronous or asynchronous.

2. `config.json`: This file contains the plugin's configuration. It's a JSON file with one required field: `enabled`. If `enabled` is set to `true`, the plugin's functions will be imported and available for use. If `enabled` is set to `false`, the plugin's functions will not be imported.

To use a plugin, ensure that it is enabled in its `config.json` file. Once enabled, the functions provided by the plugin will be automatically imported when the script is run. The AI assistant will be able to call these functions as part of the conversation.

## Creating a Plugin

To create a plugin, follow these steps:

1. Create a new directory in the 'plugins' folder. The directory name will be the plugin's name.

2. In the new directory, create a file named `functions.py`. In this file, define the functions that you want the plugin to provide. Each function should be a top-level function and should be named in a way that reflects its functionality.

3. In the same directory, create a file named `config.json`. In this file, add the following JSON:

```json
{
    "enabled": true
}
```

This will enable the plugin by default. If you want to disable the plugin, you can change `true` to `false`.

## Running the Project

To run this project, you need to follow these steps:

1. First, you need to create a `.env` file in the root directory of the project. You can do this by copying the `.env.example` file.

2. In the `.env` file, you need to provide your OpenAI API key. This should be a string, like `OPENAI_API_KEY=your_api_key_here`. Please replace `your_api_key_here` with your actual OpenAI API key.

3. Also in the `.env` file, you need to set the base URL for the OpenAI API. This should be a string, like `OPENAI_API_BASE=https://api.openai.com/v1`.

4. After saving the `.env` file, you need to install Chainlit. You can do this using pip: `pip install chainlit`.

5. Once Chainlit is installed, you can run the project using the following command: `chainlit run app.py -w`.

## Contributing

Contributions are welcome! Please read the contributing guide to learn about how you can contribute to this project.

## License

This project is licensed under the terms of the MIT license.
