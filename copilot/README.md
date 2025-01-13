# Software Copilot with Chainlit

Run the chainlit application:

```shell
chainlit run app.py
```

Then, in a separate terminal, run the frontend:

```shell
python -m http.server 80
```
By doing this, you mount the http server on port 80, so you can access the frontend at http://localhost/. It then uses the script from localhost:8000 (chainlit application) to display the widget at the bottom-right of the screen.

The application should respond "Hello World" to every message (you can implement your own logic in `app.py`).
