# Gemini Flash 2.0 Chainlit Integration

A simple web interface for interacting with Google's Gemini Flash 2.0 model using Chainlit.

## Setup

1. Clone this repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install chainlit google-generativeai python-dotenv
   ```
4. Create a `.env` file with your Gemini API key:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```
5. Create a `public/avatar` folder and add `gemini-logo.jpg` for the bot avatar

## Running the Application

```bash
chainlit run app.py
```

The application will be available at http://localhost:8000

## Project Structure

```
project/
├── app.py            # Main application code
├── chainlit.md       # Chainlit configuration file
├── .env              # Environment variables (API keys)
└── public/
    └── avatar/
        └── gemini-logo.jpg  # Custom avatar for Gemini responses
```

## Features

- Interactive chat interface
- Gemini Flash 2.0 model integration
- Custom avatar for the AI assistant
- Error handling