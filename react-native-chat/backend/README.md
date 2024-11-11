---
title: "backend"
tags: ["custom", "openai", "chainlit"]
---

## Install Chainlit and OpenAI

```shell
pip install -r requirements.txt
```

## Start the Chainlit server

Create a `./backend/.env` file:

```.env
OPENAI_API_KEY=YOUR_KEY
BASE_URL=YOUR_SITE
```

Start the server in headless mode:

```shell
cd ./backend
pip install -r requirement.txt
pip install uvicorn
uvicorn app:app --host 0.0.0.0 --port 8080
```

To create a virtual environment yourself you can use Python's venv:
```shell
python -m venv .venv
source .venv/bin/activate
.venv/bin/pip install -r requirements.txt
.venv/bin/uvicorn app:app --host 0.0.0.0 --port 8080
```

## Start the Web Client

```shell
cd ./react-web-client
npm i
npm run dev
```