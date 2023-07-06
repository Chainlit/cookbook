# Chainlit BabyAGI integration demo

This is a demo of an integration of Chainlit with BabyAGI.

The goal is to show how to use Chainlit to get more observability on agents.

## How to run

1. Install the Python dependencies:

```bash
pip install -r requirements.txt
```

2. Copy the `.env.example` file to `.env` and fill in the values (especially the `OPENAI_API_KEY`).

```bash
cp .env.example .env
```

3. Run the demo. This will open a browser window with the Chainlit UI.

```bash
chainlit run babyagi.py
```

## Credits

The code is based on the [BabyAGI](https://github.com/yoheinakajima/babyagi/) repository by [Yohei Nakajima](https://twitter.com/yoheinakajima).