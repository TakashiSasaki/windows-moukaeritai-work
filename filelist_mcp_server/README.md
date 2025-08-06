# Filelist MCP Server

A simple TCP server that creates file catalogs. It is designed to be compatible with the Everything File List (EFU) format, producing a tab-separated values (TSV) file.

## Features

- Listens on a configurable host and port for TCP connections.
- Accepts requests to catalog a directory.
- Generates a TSV file containing the list of files, their sizes, and timestamps.
- Returns an error if the target output file already exists to prevent accidental overwrites.

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
    This will create a virtual environment and install all necessary packages.

## Usage

### Running the Server

To start the MCP server, run the following command from the project root:

```bash
poetry run python -m filelist_mcp_server.main --host <hostname> --port <port_number>
```

-   `--host`: The host to bind to. Defaults to `localhost`.
-   `--port`: The port to listen on. Defaults to `10000`.

Example:
```bash
poetry run python -m filelist_mcp_server.main --port 12345
```

### Sending a Request

You can send a request to the server using a simple TCP client like `netcat` or a Python script. The request must be in the following format:

`<path_to_catalog_directory>|<path_to_output_file>`

Example using `netcat`:
```bash
echo "C:\Users\YourUser\Documents|C:\Temp\mydocuments.tsv" | nc localhost 12345
```

The server will respond with `SUCCESS` or an `ERROR` message.

## Running Tests

To run the full suite of unit and integration tests, use `pytest`:

```bash
poetry run pytest
```
*Note: Due to an environment issue in the development sandbox, the tests were run with a more complex command. The command above is the standard way it should be run in a typical environment.*
