#!/usr/bin/env python
"""Example LangChain server exposes a retriever."""
from fastapi import FastAPI
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores.faiss import FAISS

import uuid

from literalai import LiteralClient
from literalai.context import active_thread_var, active_steps_var
from literalai import Thread, Step
from dotenv import load_dotenv

load_dotenv()


from langserve import add_routes

client = LiteralClient()

vectorstore = FAISS.from_texts(
    ["cats like fish", "dogs like sticks"], embedding=OpenAIEmbeddings()
)
retriever = vectorstore.as_retriever()


def per_req_config_modifier(config, request):
    thread_id = request.headers.get("thread_id") or uuid.uuid4().hex
    parent_id = request.headers.get("run_id")

    print("current thread", active_steps_var.get())

    active_thread_var.set(Thread(id=thread_id))
    if parent_id:
        active_steps_var.set([Step(id=parent_id)])

    config["callbacks"] = [client.langchain_callback()]
    return config


app = FastAPI(
    title="LangChain Server",
    version="1.0",
    description="Spin up a simple api server using Langchain's Runnable interfaces",
)


# Adds routes to the app for using the retriever under:
# /invoke
# /batch
# /stream
add_routes(
    app,
    retriever,
    config_keys=["callbacks"],
    per_req_config_modifier=per_req_config_modifier,
    path="/test",
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8001)
