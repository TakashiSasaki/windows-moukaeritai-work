import sys
import json
from python_jsonrpc_server import jsonrpc
from . import handlers

def main():
    """
    Main server loop for stdio transport.

    Reads newline-delimited JSON-RPC messages from stdin,
    processes them using the registered handlers, and writes the
    JSON-RPC response to stdout.
    """
    # This ensures the handlers module is loaded and the @method decorators run.
    _ = handlers

    while True:
        line = sys.stdin.readline()
        if not line:
            # stdin has been closed, so we exit.
            break

        # The python-jsonrpc-server library expects a dictionary, not a raw string.
        try:
            request_dict = json.loads(line)
        except json.JSONDecodeError:
            # If the input is not valid JSON, return a Parse Error.
            response = jsonrpc.JsonRpc(error=jsonrpc.ParseError())
            print(json.dumps(response.to_dict()), flush=True)
            continue

        # The `handle_request_dict` function processes the request against the
        # methods dictionary and returns a response object.
        response = jsonrpc.handle_request_dict(request_dict, handlers.methods)

        # A response is None for notifications (which don't require a response).
        if response is not None:
            print(json.dumps(response.to_dict()), flush=True)

if __name__ == "__main__":
    main()
