# Chainlit + OpenAI Responses Demo (Multimodal • Reasoning • Streaming • Functions)

A lean Chainlit app that wires the **OpenAI Responses API** to a real **local Python executor** with **multimodal I/O (text, images, files)**, **reasoning traces**, **token+function streaming**, and **tool functions** (web search preview, image generation, Python runner, file ops, optional file-search).  &#x20;

---

## Features (at a glance)

* **Multimodal input**: accepts text, images, and file uploads in one message.&#x20;
* **Multimodal output**: previews **images** inline and **CSV DataFrames** (with a download link) or falls back to readable text. &#x20;
* **Reasoning**: configurable effort + **streamed reasoning summary** you can show in the UI when available. &#x20;
* **Streaming**: assistant text streams token-by-token; **function call metadata & arguments stream** too, so you can live-render generated Python code.  &#x20;
* **Functions / Tools**: registered tools include `execute_python_code`, `upload_file_to_workspace`, `list_workspace_files`, simple calculator, **web\_search\_preview**, **image\_generation**, and optional **file\_search** when a vector store is present.  &#x20;
* **Per-chat workspace**: each chat gets its own `.files/{session_id}/pyws` folder; Python runs there and files persist for the chat’s lifetime.&#x20;
* **Nice UX**: progress steps for web search, image gen, and Python runs; optional full conversation/“reasoning summary” panels. &#x20;

---

## What’s in the repo

* **`app.py`** — Chainlit lifecycle, dev-prompt injection on first turn, vector-store hookup on upload, Responses **streaming loop** (text + function args), live “Python Code Being Generated” pane, and a multi-iteration tool loop.    &#x20;
* **`tools.py`** — Tool registry and implementations:

  * `execute_python_code` (**persistent workspace**, returns stdout/stderr + collected files).&#x20;
  * `upload_file_to_workspace` / `list_workspace_files` helpers.&#x20;
  * File renderer that shows **images inline**, **CSV as DataFrame**, and **text previews** with download buttons.  &#x20;

---

## Quick start

```bash
python -m venv .venv && source .venv/bin/activate         # Windows: .venv\Scripts\activate
pip install chainlit openai pandas matplotlib
export OPENAI_API_KEY=sk-...                               # Windows PowerShell: $env:OPENAI_API_KEY="sk-..."
chainlit run app.py -w
```

Open [http://localhost:8000](http://localhost:8000).

---

## How it works

1. **Dev prompt + settings**
   First turn injects your developer instructions; reasoning effort and summary are toggled in settings. &#x20;

2. **Multimodal in**
   You can send text, images, and files together; non-image files are converted to **function calls** to place them in the workspace. &#x20;

3. **Streaming loop**
   The app calls `responses.create(stream=True)` and processes an event stream:

   * assistant text tokens,
   * function call *creation* events,
   * **function argument deltas** (used to live-render code for `execute_python_code`).  &#x20;

4. **Tool execution**
   Detected calls are executed, then their outputs are returned via `function_call_output` and the loop continues until the model is done.&#x20;

5. **Results rendering**
   Python runs can emit images/CSVs/text; these are previewed inline and attached as downloads. &#x20;

6. **Optional RAG**
   If you upload docs at start, the app creates a vector store and enables the **file\_search** tool for the model. &#x20;

---

## Configuration

* **Model**: change the model in `_ask_gpt`.&#x20;
* **Reasoning**: set effort, enable summary.&#x20;
* **Workspace**: path = `.files/{session_id}/pyws`; auto-cleaned on chat end. &#x20;
* **Tools**: edit `build_tools(...)` to add/remove tools; file-search is gated on vector store presence. &#x20;

---

## Troubleshooting

* **No code preview while functions run** → ensure you’re calling Responses with `stream=True` and watch for `function_call_arguments.delta` events. &#x20;
* **CSV not rendering as a table** → pandas must be importable; otherwise it falls back to a text preview. &#x20;
* **Files didn’t persist** → they persist for the chat; cleanup runs on `@cl.on_chat_end`.&#x20;

---

## Security

Python executes **locally** inside the per-chat workspace. Treat generated code as untrusted; time limits are applied in the executor and files are confined to that directory. (See the Python tool descriptions and file-handling utilities.) &#x20;

---

## File map

* `app.py` — chat lifecycle, dev prompt, vector store & **file\_search**, event-driven streaming, multi-iteration function loop, code preview.  &#x20;
* `tools.py` — tool registry, Python executor, upload/list helpers, image/CSV/text previewers, progress + reasoning summary steps.  &#x20;

Add a license (MIT recommended) and you’re set.
