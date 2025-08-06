# Filelist MCP Server

A server that implements the Model Context Protocol (MCP) to provide a file cataloging tool.

This server communicates over `stdio` using JSON-RPC 2.0, as per the MCP specification. It exposes a `catalog/create` tool that can be called by any MCP-compliant client.

## Features

-   Implements `stdio` and `http` transports for the Model Context Protocol.
-   Uses JSON-RPC 2.0 for all communication.
-   Exposes a `catalog/create` tool to recursively scan a directory and create a file list.
-   The output is a TSV file compatible with the Everything File List (EFU) format.

## Installation

This project is managed with [Poetry](https://python-poetry.org/).

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd filelist-mcp-server
    ```

2.  **Install dependencies:**
    ```bash
    poetry install
    ```
    This will create a virtual environment and install all packages, including a command-line script for the server.

## Usage

The server can be run in two modes: `stdio` or `http`.

### Stdio Mode (Default)

The server is designed to be run as a subprocess by an MCP client. This is the default mode.

```bash
# This runs the server in stdio mode
poetry run mcp-server stdio
```

The server will then wait for JSON-RPC messages on its standard input.

### HTTP Mode

The server can also run as a persistent HTTP server.

```bash
# This runs the server in http mode on port 8080
poetry run mcp-server http --host localhost --port 8080
```

The server will then listen for JSON-RPC messages via HTTP POST requests to the `/mcp` endpoint.

### Example Interaction

1.  **Client sends `initialize` request:**
    ```json
    {"jsonrpc": "2.0", "method": "initialize", "params": {"capabilities": {}}, "id": 1}
    ```

2.  **Server responds with its capabilities:**
    ```json
    {"jsonrpc": "2.0", "id": 1, "result": {"capabilities": {"tools": [{"name": "catalog/create", "description": "...", "parameters": {...}}]}}}
    ```

3.  **Client calls the `catalog/create` tool:**
    ```json
    {"jsonrpc": "2.0", "method": "catalog/create", "params": {"target_dir": "/path/to/docs", "output_file": "/tmp/docs.tsv"}, "id": 2}
    ```

4.  **Server responds with success:**
    ```json
    {"jsonrpc": "2.0", "id": 2, "result": {"status": "success", "message": "Catalog created for /path/to/docs"}}
    ```

## Running Tests

To run the suite of unit tests:

```bash
poetry run pytest
```
*Note: The integration tests for both the stdio (`tests/test_protocol.py`) and http (`tests/test_http.py`) transports currently fail when run in some environments (like the development sandbox). This is due to a persistent environment issue where the `poetry run` command fails to make installed dependencies available to the test process, causing a `ModuleNotFoundError`. The core unit tests (`tests/test_catalog.py`) are passing, and the server and test logic is believed to be correct.*
