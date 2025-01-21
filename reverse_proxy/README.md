# Reverse proxy

Run chainlit on a prefix (root-path) behind [Caddy](https://caddyserver.com/) as a reverse proxy.

## Quick start
1. Install Python requirements with your favourite package manager (like uv or poetry) into your favourite (virtual) environment.
2. [Install Caddy](https://caddyserver.com/docs/install).
3. Run uvicorn and Caddy with: `./start.sh`
4. Find Chainlit at `http://127.0.0.1:8080/proxy/chainlit`.
