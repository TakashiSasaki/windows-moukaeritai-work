import sys
import json
import argparse
from python_jsonrpc_server import jsonrpc
from . import handlers
from . import http_server

def run_stdio_server():
    """
    The main loop for the stdio transport.
    Reads newline-delimited JSON-RPC messages from stdin, processes them,
    and writes responses to stdout.
    """
    # This ensures the handlers module is loaded and the @method decorators run.
    _ = handlers
    while True:
        line = sys.stdin.readline()
        if not line:
            break
        try:
            request_dict = json.loads(line)
        except json.JSONDecodeError:
            response = jsonrpc.JsonRpc(error=jsonrpc.ParseError())
            print(json.dumps(response.to_dict()), flush=True)
            continue

        response = jsonrpc.handle_request_dict(request_dict, handlers.methods)
        if response is not None:
            print(json.dumps(response.to_dict()), flush=True)

def main():
    """
    Main entry point for the server.
    Parses command-line arguments to start the server with the specified transport.
    """
    parser = argparse.ArgumentParser(description="Filelist MCP Server")
    subparsers = parser.add_subparsers(dest="transport", required=True, help="The transport protocol to use.")

    # Sub-parser for the 'stdio' transport
    parser_stdio = subparsers.add_parser("stdio", help="Run the server over stdio.")

    # Sub-parser for the 'http' transport
    parser_http = subparsers.add_parser("http", help="Run the server over HTTP.")
    parser_http.add_argument(
        "--host",
        type=str,
        default="localhost",
        help="Host to bind the HTTP server to (default: localhost)."
    )
    parser_http.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Port for the HTTP server to listen on (default: 8080)."
    )

    args = parser.parse_args()

    if args.transport == "stdio":
        run_stdio_server()
    elif args.transport == "http":
        # The http_server module will contain the logic to start aiohttp
        http_server.start(host=args.host, port=args.port)

if __name__ == "__main__":
    main()
