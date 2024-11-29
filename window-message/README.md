# Window Message with Chainlit

Run the chainlit application on port 8000:

```shell
chainlit run app.py -h -c --port 8000
```

Then open `frontend\dist\index.html` in your browser, which includes Chainlit inside an iframe.

Click on the `Send message to iframe` button to send a message to the server, handled using `@cl.on_window_message`.

The server will send back a message to the parent window using `cl.send_window_message` when receiving either a window message or a regular message.

The last message received by the window is displayed above the button.
