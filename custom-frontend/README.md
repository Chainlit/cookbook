# Custom frontend with Chainlit!

The Chainlit websocket client is available in the [@chainlit/react-client](https://www.npmjs.com/package/@chainlit/react-client) npm package.

## Install Chainlit and OpenaI

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
