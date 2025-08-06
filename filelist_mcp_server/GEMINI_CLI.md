# Using the MCP Server with Gemini CLI

This guide explains how to integrate the Filelist MCP Server with a tool like Gemini CLI.

## Integration Strategy

The server implements the Model Context Protocol over `stdio`. A compliant client like Gemini CLI should be configured to launch the `mcp-server` executable as a subprocess. The client then communicates with the server by writing JSON-RPC messages to the server's `stdin` and reading responses from its `stdout`.

## Configuration

The client needs to know how to start the server. After installing the package with `poetry install`, the executable `mcp-server` will be available inside the project's virtual environment.

A Gemini CLI configuration might look something like this, defining a new "provider" or "backend" that points to the server executable.

### Sample Gemini CLI Backend Configuration

The `gemini-cli.config.toml` file in this repository provides a sample of how a CLI tool could be configured to use this server. A real integration would involve placing a similar configuration in a path that your Gemini CLI tool recognizes.

```toml
# In a hypothetical file like ~/.config/gemini/backends.toml

[mcp_backend.filelist]
# Command to execute to start the server.
# Gemini CLI should resolve this path, potentially using the active virtualenv.
executable = "mcp-server"

# The protocol this backend uses.
protocol = "mcp"

# The transport mechanism.
transport = "stdio"
```

## Usage

Once the backend is configured, Gemini CLI would handle the process management and communication. The user could then access the tools provided by the server through the CLI's interface.

For example, to call the `catalog/create` tool, the user might run a command like:

```sh
# Hypothetical Gemini CLI command
gemini call-tool filelist catalog/create --params '{"target_dir": "/my/docs", "output_file": "/tmp/catalog.tsv"}'
```

The CLI would then perform the following steps in the background:
1.  Start the `mcp-server` process.
2.  Send the `initialize` handshake.
3.  Send the `catalog/create` request to the server's `stdin`.
4.  Read the response from the server's `stdout`.
5.  Print the result to the user.
6.  Send `shutdown` and `exit` notifications to terminate the server process.
