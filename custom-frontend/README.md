---
title: 'Custom frontend with Chainlit!'
tags: ['custom', 'frontend', 'chainlit']
---

# Custom frontend with Chainlit!

The Chainlit websocket client is available in the [@chainlit/react-client](https://www.npmjs.com/package/@chainlit/react-client) npm package.


https://github.com/Chainlit/cookbook/assets/13104895/5cc20490-2150-44da-b016-7e0e2e12dd52


## Install Chainlit and OpenAI

```shell
pip install -U chainlit openai
```

## Start the Chainlit server

Create a `./chainlit-backend/.env` file:

```.env
OPENAI_API_KEY=YOUR_KEY
```

Start the server in headless mode:

```shell
cd ./chainlit-backend
chainlit run app.py -h
```

## Start the React app

```shell
cd ./frontend
npm i
npm run dev
```
