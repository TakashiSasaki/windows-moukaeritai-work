# Using the MCP Server with Google Gemini CLI

This guide explains how to configure and use the Filelist MCP Server with the official Google Gemini CLI.

## Configuration

The Google Gemini CLI discovers MCP servers through a configuration file. This file must be named `settings.json` and placed in either:
-   `~/.gemini/` (for global settings that apply everywhere)
-   `.gemini/` inside your current project's root (for project-specific settings)

You need to add an entry for this server under the `mcpServers` object in the JSON file.

### 1. Install the Server

First, ensure you have installed the server and its dependencies using Poetry from the project's root directory:

```bash
poetry install
```

This command installs the necessary packages and creates a script named `mcp-server` inside the project's virtual environment.

### 2. Configure `settings.json`

The key to a successful configuration is telling the Gemini CLI exactly how to run the `mcp-server` script. Since this is a Poetry project, the most reliable way is to use the `poetry run` command.

Below are two scenarios for your `settings.json` configuration.

#### Scenario A: Running Gemini CLI from Anywhere (Recommended)

This approach works regardless of your current directory. You must provide the **absolute path** to the server's project directory.

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

#### Scenario B: Running Gemini CLI from the Project Directory

If you always run the `gemini` command from within the `filelist-mcp-server` directory, you can use a simpler relative path for `cwd`.

Create or open a `.gemini/settings.json` file **inside the `filelist-mcp-server` project root** and add:

```json
{
  "mcpServers": {
    "filelist_server": {
      "command": "poetry",
      "args": ["run", "mcp-server"],
      "cwd": ".",
      "trust": true
    }
  }
}
```

**Details:**
-   `"cwd": "."` tells the CLI to run the command from the current directory, which is assumed to be the project root.

## Usage

Once configured, start the Gemini CLI. It will discover the `filelist_server` and its `catalog/create` tool.

You can then ask Gemini to use the tool in your prompts.

**Example Prompt:**

> Use the filelist_server to create a catalog of my documents directory at `/Users/me/Documents` and save it to `/tmp/my_docs_catalog.tsv`.

You can also use the `/mcp` command in the Gemini CLI to see the status of your connected servers and their tools.
