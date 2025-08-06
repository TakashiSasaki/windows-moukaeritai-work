# MCP Server Implementation

This server implements the Model Context Protocol (MCP) to expose a file cataloging tool.

## Transport

The server uses the `stdio` transport layer. It expects a client to launch it as a subprocess and communicate by writing newline-delimited JSON-RPC 2.0 messages to its standard input (`stdin`) and reading responses from its standard output (`stdout`).

## Supported Methods

The server supports the following standard and custom MCP methods.

### `initialize`

**Description**: Standard MCP handshake. The client sends its capabilities, and the server responds with its own.

**Response**: The server declares that it provides one tool: `catalog/create`.

```json
{
  "capabilities": {
    "tools": [
      {
        "name": "catalog/create",
        "description": "Creates a catalog of all files in a directory, saving it as a TSV file.",
        "parameters": {
          "type": "object",
          "properties": {
            "target_dir": {
              "type": "string",
              "description": "The absolute path of the directory to catalog."
            },
            "output_file": {
              "type": "string",
              "description": "The absolute path where the output TSV file will be saved."
            }
          },
          "required": ["target_dir", "output_file"]
        }
      }
    ]
  }
}
```

### `shutdown`

**Description**: Standard MCP notification that the client is preparing to shut down. The server should perform any cleanup. It does not send a response.

### `exit`

**Description**: Standard MCP notification that the client has shut down and the server process should now terminate.

### `catalog/create` (Custom Tool)

**Description**: This is the custom tool provided by the server. It scans a directory and creates a TSV file catalog.

**Parameters**:
- `target_dir` (string): The absolute path of the directory to catalog.
- `output_file` (string): The absolute path where the output file will be saved.

**Successful Response**:
```json
{
  "status": "success",
  "message": "Catalog created for <target_dir>"
}
```

**Error Responses**:
- `code: 1001`: Output file already exists.
- `code: 1002`: Target directory not found.
- `code: -32602` (Invalid Params): A required parameter was missing.
