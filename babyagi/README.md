Title : BabyAGI
Tags : [autonomous-agent]

# Chainlit BabyAGI integration demo

This is a demo of an integration of Chainlit with BabyAGI.

The goal is to show how to use Chainlit to get more observability on agents.

https://github.com/Chainlit/cookbook/assets/13104895/57d1d9af-62a0-4f67-a530-1f0a3fc93488

## How to run

1. Install the Python dependencies:

```bash
pip install -r requirements.txt
```

2. Copy the `.env.example` file to `.env` and fill in the values (especially the `OPENAI_API_KEY` for the LLM API and the `OBJECTIVE` for the AI goal).

```bash
cp .env.example .env
```

3. Run the demo. This will open a browser window with the Chainlit UI.

```bash
chainlit run babyagi.py
```

## Credits

The code is based on the [BabyAGI](https://github.com/yoheinakajima/babyagi/) repository by [Yohei Nakajima](https://twitter.com/yoheinakajima).

