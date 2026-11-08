# Standalone MCP Server

This repository includes an optional standalone [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server. It uses **Streamable HTTP** and listens locally at `http://127.0.0.1:8050/mcp` by default.

## Requirements

- Python 3
- A Tavily API key for the `fetch_web_search` tool.

## Setup and Run

Create a separate virtual environment, install the dependencies, and start the server:

```sh
uv venv .venv
source .venv/bin/activate
uv sync
TAVILY_API_KEY=<env-key> uv run python server.py
```

The server will be available at:

[http://127.0.0.1:8050/mcp](http://127.0.0.1:8050/mcp)

`TAVILY_API_KEY` is required only for the `fetch_web_search` tool.

You can configure the server's host and port using the `MCP_HOST` and `MCP_PORT` environment variables.

For example, to run the server on port `8000`:

```sh
MCP_PORT=8000 .venv/bin/python server.py
```

## Available MCP Features

The server exposes three MCP tools and the `info://tool-guide` resource.

The Tavily API key is used exclusively by the `fetch_web_search` tool.

## Inspect the Server

To inspect the server's tool schemas and call its tools using the MCP Inspector:

1. Start the MCP server.
2. Open another terminal and run:

   ```sh
   npx -y @modelcontextprotocol/inspector
   ```

3. In the MCP Inspector, select **Streamable HTTP** as the transport type.
4. Connect to the following MCP endpoint:

   [http://127.0.0.1:8050/mcp](http://127.0.0.1:8050/mcp)

## Expose the Server with ngrok [OPTIONAL]

For temporary external access during development, keep the MCP server running and start ngrok in another terminal:

```sh
ngrok http 8050
```

ngrok will generate an HTTPS forwarding URL. In your MCP client, use the generated URL with `/mcp` appended.

For example:

```text
https://your-ngrok-domain.ngrok.app/mcp
```

**Security note:** The ngrok URL is publicly accessible while the tunnel is active. Configure appropriate authentication and access controls before exposing the server beyond your local development environment. Stop the ngrok tunnel when you are finished.

## Security and Configuration

- Keep API keys and other secrets out of source control. Use environment variables or a local `.env` file excluded through `.gitignore`.
- Do not commit personal or temporary ngrok URLs.
- When exposing the server beyond your local machine, protect access with appropriate authentication and TLS.
- Keep the server bound to `127.0.0.1` for local-only access.
- Set `MCP_HOST` to a network-accessible interface only when remote access is required.
