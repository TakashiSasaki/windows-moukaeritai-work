# Filelist MCP Server

A server that implements the Model Context Protocol (MCP) to provide a file cataloging tool.

This server communicates over `stdio` using JSON-RPC 2.0, as per the MCP specification. It exposes a `catalog/create` tool that can be called by any MCP-compliant client.

## Features

-   Implements the `stdio` transport for the Model Context Protocol.
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

The server is designed to be run as a subprocess by an MCP client (e.g., an AI agent, an IDE extension). The client communicates with the server by writing JSON-RPC messages to the server's `stdin` and reading responses from its `stdout`.

To run the server manually, you can use the script installed by Poetry:

```bash
poetry run mcp-server
```

The server will then wait for JSON-RPC messages on its standard input.

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
*Note: The integration test for the stdio subprocess (`tests/test_protocol.py`) is currently failing in some environments due to issues with how the subprocess's virtualenv and PYTHONPATH are handled. The core unit tests (`tests/test_catalog.py`) are passing.*
