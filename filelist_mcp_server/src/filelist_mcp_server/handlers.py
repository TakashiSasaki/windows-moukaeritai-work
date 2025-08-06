import sys
from python_jsonrpc_server import jsonrpc
from .catalog import create_catalog, OutputFileExistsError

methods = {}

def method(name):
    """A decorator to register a function as a JSON-RPC method."""
    def decorator(f):
        methods[name] = f
        return f
    return decorator

@method("initialize")
def initialize(params):
    """
    Handles the MCP initialize request and returns the server's capabilities.
    """
    # The server declares the tools it provides.
    # The format follows the MCP specification for capabilities.
    return {
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

@method("shutdown")
def shutdown():
    """
    Handles the shutdown notification. The client is about to exit.
    The server should not exit yet, but can perform cleanup.
    This is a notification, so it must not return a value.
    """
    # For this simple server, no specific cleanup is needed.
    pass

@method("exit")
def exit_method():
    """
    Handles the exit notification. The server process should terminate.
    """
    sys.exit(0)

@method("catalog/create")
def catalog_create(params):
    """
    The custom tool method that creates the file catalog.

    It raises specific JSON-RPC errors for known failure modes.
    """
    try:
        # Validate that required parameters are present.
        target_dir = params['target_dir']
        output_file = params['output_file']
    except KeyError as e:
        # Invalid Params error code is -32602
        raise jsonrpc.InvalidParams(f"Missing parameter: {e}")

    try:
        create_catalog(target_dir, output_file)
        return {"status": "success", "message": f"Catalog created for {target_dir}"}
    except OutputFileExistsError as e:
        # Using a custom error code in the application-defined range
        raise jsonrpc.JsonRpcError(code=1001, message=str(e))
    except FileNotFoundError as e:
        # Using another custom error code
        raise jsonrpc.JsonRpcError(code=1002, message=str(e))
    except Exception as e:
        # For any other unexpected errors, use a generic server error.
        # Server error code is -32000
        raise jsonrpc.ServerError(f"An unexpected error occurred: {e}")
