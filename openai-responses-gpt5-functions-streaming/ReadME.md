# OpenAI *Responses* API — GPT-5 Function Calls + Streaming

This recipe shows how to use **OpenAI’s experimental `responses` endpoint** with

- ⏩ **Server-side streaming** (no latency between tokens)
- 🔧 **Function calling** (tools) with a multi-step loop
- 💾 Conversation continuity via **`previous_response_id`**
- 🖼️ A Chainlit debug step that prints the **full conversation history**
- 🗃️ Simple in-memory cache for tool outputs (O(1) lookup)

It answers in classic *Ned Flanders* style just for fun—feel free to tweak the `instructions` string in `app.py`.

---

## Quick-start

```bash
# 1. Install deps into a fresh venv (optional but recommended)
python -m venv .venv
source .venv/bin/activate       # or .\.venv\Scripts\activate on Windows
pip install -r requirements.txt

# 2. Export your key (or create a .env file that Chainlit will pick up)
export OPENAI_API_KEY=<your key>

# 3. Run the app
chainlit run app.py -w
