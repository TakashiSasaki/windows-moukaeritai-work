# Using the MCP Server with Google Gemini CLI

This guide explains how to configure and use the Filelist MCP Server with the official Google Gemini CLI, using either the `stdio` or `http` transport.

## Configuration

The Google Gemini CLI discovers MCP servers through a configuration file named `settings.json`, located in `~/.gemini/` or your project's `.gemini/` directory.

### 1. Install the Server

First, ensure you have installed the server and its dependencies using Poetry:

```bash
poetry install
```

This command installs the necessary packages and creates a script named `mcp-server` inside the project's virtual environment.

### 2. Configure `settings.json`

You can configure the server to be used over `stdio` or `http`.

#### Option 1: `stdio` Transport (Recommended for local use)

This approach runs the server as a subprocess. You must provide the **absolute path** to the server's project directory in the `cwd` field.

Create or open your `~/.gemini/settings.json` file and add the following:

```json
{
  "mcpServers": {
    "filelist_server": {
      "command": "poetry",
      "args": ["run", "mcp-server"],
      "cwd": "/path/to/your/cloned/filelist-mcp-server",
      "trust": true
    }
  }
}
```

**Action Required:**
-   You **must** replace `/path/to/your/cloned/filelist-mcp-server` with the actual, full path to where you have cloned this project on your machine. For example: `C:\Users\YourUser\Projects\filelist-mcp-server` or `/home/youruser/dev/filelist-mcp-server`.

#### Option 2: `http` Transport

For this option, you must first start the server manually in a separate terminal.

```bash
# In a terminal, navigate to the project directory and run:
poetry run mcp-server http --host localhost --port 8080
```

Then, configure your `~/.gemini/settings.json` to point to the server's URL:

```json
{
  "mcpServers": {
    "filelist_server_http": {
      "httpUrl": "http://localhost:8080/mcp",
      "trust": true
    }
  }
}
```

**Details:**
-   `"httpUrl"`: This must match the host and port where your server is running.

## Usage

Once configured, start the Gemini CLI. It will discover the `filelist_server` and its `catalog/create` tool.

You can then ask Gemini to use the tool in your prompts.

**Example Prompt:**

> Use the filelist_server to create a catalog of my documents directory at `/Users/me/Documents` and save it to `/tmp/my_docs_catalog.tsv`.

You can also use the `/mcp` command in the Gemini CLI to see the status of your connected servers and their tools.
