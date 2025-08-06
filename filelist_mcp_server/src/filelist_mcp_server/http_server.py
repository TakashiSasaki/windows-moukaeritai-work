import json
from aiohttp import web
from python_jsonrpc_server import jsonrpc
from . import handlers

async def mcp_handler(request):
    """
    Handles incoming HTTP requests to the /mcp endpoint.
    It processes JSON-RPC requests received via POST.
    """
    if request.method != "POST":
        # The spec allows GET for SSE, but we are not implementing the
        # server-to-client notification part, so we only allow POST.
        return web.Response(status=405, text="Method Not Allowed")

    try:
        request_dict = await request.json()
    except json.JSONDecodeError:
        # If the request body is not valid JSON.
        response_dict = jsonrpc.JsonRpc(error=jsonrpc.ParseError()).to_dict()
        return web.json_response(response_dict, status=400)

    # Reuse the same dispatch logic from the stdio server.
    # The `handle_request_dict` function will call the appropriate
    # method from our `handlers.py` file.
    response = jsonrpc.handle_request_dict(request_dict, handlers.methods)

    if response:
        # For requests that expect a response, send it back as JSON.
        return web.json_response(response.to_dict())
    else:
        # For notifications, the spec says to return HTTP 202 Accepted.
        return web.Response(status=202)

def start(host, port):
    """
    Configures and starts the aiohttp web server.
    """
    # This ensures the handlers module is loaded and the @method decorators run.
    _ = handlers

    app = web.Application()
    # Route all requests to /mcp to our single handler.
    app.router.add_route('POST', '/mcp', mcp_handler)

    print(f"Starting HTTP MCP server on http://{host}:{port}/mcp")
    # web.run_app is a convenient way to run the aiohttp server.
    web.run_app(app, host=host, port=port)
