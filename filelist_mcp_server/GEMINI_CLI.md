# Using the MCP Server with Gemini CLI

This guide explains how to interact with the Filelist MCP Server from a command-line interface like Gemini CLI. We assume that your CLI has a tool capable of opening TCP connections, such as `netcat` (`nc`), `ncat`, or a similar utility.

## Prerequisites

1.  **Start the MCP Server:** Ensure the MCP server is running. You can start it using the command from the main `README.md`:
    ```sh
    # From the project's root directory
    poetry run python -m filelist_mcp_server.main --host localhost --port 10000
    ```
    You can change the host and port as needed.

2.  **TCP Client Tool:** You need a command-line TCP client. We will use `nc` (`netcat`) in the examples below.

## Sending a Catalog Request

To request a file catalog, you need to send a formatted string to the server. The format is `TARGET_DIRECTORY|OUTPUT_FILE`.

You can use the `echo` command to create the request string and pipe it directly to your TCP client.

### Example on Linux / macOS

```sh
# Request to catalog the '/home/user/documents' directory
# and save the output to '/tmp/docs.tsv'
echo "/home/user/documents|/tmp/docs.tsv" | nc localhost 10000
```

### Example on Windows (using PowerShell)

If you have a `netcat` equivalent on Windows, the command is similar. Here's an example using PowerShell with a hypothetical `nc.exe`:

```powershell
# Request to catalog 'C:\Users\Admin\Documents'
# and save to 'C:\Temp\catalog.tsv'
echo "C:\Users\Admin\Documents|C:\Temp\catalog.tsv" | nc.exe localhost 10000
```

## Reading the Response

The server will immediately send a response back to the same TCP connection. The client tool will print this response to your standard output.

-   If you see `SUCCESS`, the operation is complete.
-   If you see `ERROR: ...`, the message will describe what went wrong.

```sh
# Successful execution
$ echo "/home/user/documents|/tmp/docs.tsv" | nc localhost 10000
SUCCESS

# Failed execution (if /tmp/docs.tsv already exists)
$ echo "/home/user/documents|/tmp/docs.tsv" | nc localhost 10000
ERROR: Output file already exists: /tmp/docs.tsv
```
