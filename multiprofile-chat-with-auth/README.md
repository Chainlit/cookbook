# Home AI

* This demo illustrates how to use [Chainlit](https://github.com/Chainlit/chainlit) to build chatbots with LLMs the big
  three AI providers: OpenAI, Anthropic, and Gemini.
* [Live Demo](https://homeai.chainlit.com)

## Features

- Multiple user profiles
- Integration with [OpenAI](https://openai.com/), [Anthropic](https://www.anthropic.com/)
  and [Gemini](https://www.gemini.com/) chat providers
- Chat settings
- Authentication
- Custom logo and favicon
- Custom theme

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/mungana-ai/homeai.git
   cd homeai
   ```

2. Create a virtual environment:

   ```bash
   python -m venv venv         # We assume you are using at least Python 3.10
   source venv/bin/activate    # For Unix-based systems
   venv\Scripts\activate.bat   # For Windows
   ```

3. Install the package and its dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Configuration

1. Rename the provided `.env.example` file into `.env` in the project root directory.

2. Update the necessary configuration variables to the `.env` file. The following variables are required:

   ```bash
   DEFAULT_USER_PASSWORD=your_default_user_password
   CHAINLIT_AUTH_SECRET=your_64_char_chainlit_auth_secret_for_signing_tokens
   LITERAL_API_KEY=your_literal_api_key_for_storing_chat_history
   
   # Optional: At least one of the following chat providers is required
   OPENAI_API_KEY=your_openai_api_key
   ANTHROPIC_API_KEY=your_anthropic_api_key
   GOOGLE_API_KEY=your_google_api_key
   
   # Optional
   DEFAULT_USERNAME=your_default_username  # Default: "admin"
   ```

    > **Hints:** You can generate a 64-character secret key using the following command: `chainlit create-secret`. To
    > obtain an API key for [Literal](https://literal.chainlit.com), sign up for an account and create a new project.

## Usage

To run the Chainlit app, use the following command:

```bash
chainlit run app.py --host 0.0.0.0 --port 5500
```

* You app should now be accessible at `http://localhost:5500`

## Project Structure

The project structure is organized as follows:

- `src/`: Contains the main application code.
- `.chainlit/`: Contains the Chainlit configuration files.
- `public/`: Contains the static files for custom logos and favicons.
- `app.py`: The main application entry point.
- `.env.example`: Stores the environment variables template.
- `requirements.txt`: Lists the project dependencies.
- `chainlit.md`: Provides documentation and instructions for the project.

## Issues

If you have any questions or inquiries, please contact [N Nemakhavhani](mailto://endeesa@yahoo.com). Bugs and issues can
be reported on the [GitHub Issues]() page.

## License

This project is licensed under the MIT License. You are free to use, modify, and distribute the code as you see fit.

## Contributions

Contributions are welcome! If you would like to contribute to the project, please fork the repository and submit a pull
request.


## Links

* [OpenAI API](https://platform.openai.com/docs/quickstart)
* [Anthropic API](https://docs.anthropic.com/en/api/getting-started)
* [Gemini API](https://ai.google.dev/gemini-api/docs/api-key)
* [Literal API](https://cloud.getliteral.ai/)