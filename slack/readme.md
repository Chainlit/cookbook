# Slack Socket Mode Example

A minimal, self‑contained demo that shows how to connect a **Chainlit** app to Slack via **Socket Mode** (WebSockets). It echoes each user message and greets the sender by e‑mail.

---

## Prerequisites

| Requirement | Notes |
|-------------|-------|
| Python ≥ 3.9 | Any recent 3.x works. |
| Slack workspace | You need permission to create and install an app. |
| Slack app tokens | *Bot* token (`SLACK_BOT_TOKEN`), *Socket‑mode* token (`SLACK_WEBSOCKET_TOKEN`), and *Signing Secret* (`SLACK_SIGNING_SECRET`). |

> **Tip:** In the Slack dashboard, enable **Socket Mode** and add the *`connections:write`* scope to generate the websocket token.

---

## Project layout

```
examples/slack_socket_mode/
│ .env.example          # placeholder for the three Slack tokens
│ app.py                # Chainlit echo bot
│ requirements.txt      # exact Python deps
└ README.md             # this file
```

---

## Quick start

```bash
# 1 – enter the example directory (from repo root)
cd examples/slack_socket_mode

# 2 – create and activate a virtualenv (optional but recommended)
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 3 – install deps
pip install -r requirements.txt

# 4 – add your real tokens
cmp .env.example .env      # then edit .env

# 5 – run the bot
python app.py
```

Invite the bot to a channel or send it a direct message in Slack. It should reply with something like:

> *Hi john.doe@example.com, I have received the following message:* **hello!**

---

## How it works

`app.py` spins up a Chainlit application and, if `SLACK_WEBSOCKET_TOKEN` is present, it starts Slack’s `AsyncSocketModeHandler`. Messages received over the websocket are handled in the `@on_message` function, which:

1. Detects the client is Slack (`client_type == "slack"`).
2. Reads the sender’s e‑mail from the metadata.
3. Sends an acknowledgement back to the same channel.

The HTTP event‑based handler remains available when only `SLACK_BOT_TOKEN` & `SLACK_SIGNING_SECRET` are defined.

---

## Troubleshooting

* **`xoxb-*** or **`xapp-*** token invalid** – make sure the app is installed in the workspace and the token is copied correctly.
* **Bot doesn’t respond** – check that it’s added to the channel and has the chat:write scope.
* **Firewall / proxy issues** – Socket Mode uses outbound WebSocket connections on port 443; ensure they’re not blocked.

---

## License

This example inherits the repository’s license.
