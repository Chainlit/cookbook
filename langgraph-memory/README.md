# LangGraph Memory

The `app.py` starts a Chainlit application with a LangGraph workflow initialized with a memory. 

The example uses authentication (put a Chainlit secret in your `.env`!) and persistence from the official data layer. 
It should work with any data layer since we only rely on the context's thread ID. 

```
cp .env.example .env
pip install -r requirements.txt
chainlit run app.py
```

Login with `admin`/`admin` and start a conversation. 
Switch conversations and resume a previous one, the assistant is still aware of your previous questions. 

Currently, there is one workflow to serve all user requests. It seems to be the recommended way by LangGraph since they support memory at a thread level. 

The example showcases the use of `MemorySaver` which is "an in-memory checkpoint saver". 
So if you restart your Chainlit application, the LangGraph workflow is a new one with a new memory saver. 
