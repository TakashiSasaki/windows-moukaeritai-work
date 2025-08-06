# MCP Server Methods

The MCP server listens for TCP connections and processes a single type of request to generate a file catalog.

## `create_catalog`

This is the primary and only method supported by the server. It is invoked by sending a specially formatted string over a TCP socket.

### Request Format

The request must be a UTF-8 encoded string with the following format:

`<TARGET_DIRECTORY>|<OUTPUT_FILE_PATH>`

-   **`TARGET_DIRECTORY`**: The absolute path to the directory you want to catalog.
-   **`|`**: A pipe character acting as a separator.
-   **`OUTPUT_FILE_PATH`**: The absolute path where the resulting TSV catalog file should be saved. This file must not already exist.

### Response Format

The server will send back a simple UTF-8 encoded string to indicate the result:

-   **`SUCCESS`**: If the catalog was created successfully.
-   **`ERROR: <details>`**: If any error occurred. The `<details>` part will contain a human-readable description of the error (e.g., "Output file already exists", "Target directory not found").

### Example

**Request:**
`C:\MyData\Photos|C:\Temp\photo_catalog.tsv`

**Successful Response:**
`SUCCESS`

**Error Response (if `C:\Temp\photo_catalog.tsv` already exists):**
`ERROR: Output file already exists: C:\Temp\photo_catalog.tsv`
