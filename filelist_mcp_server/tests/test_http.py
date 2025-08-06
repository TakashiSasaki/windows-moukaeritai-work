import pytest
import asyncio
from aiohttp import web
import httpx
from unittest.mock import MagicMock, AsyncMock


# A fixture to create a temporary directory for test files
@pytest.fixture
def temp_dir(tmp_path):
    return tmp_path

@pytest.mark.asyncio
async def test_http_server_full_lifecycle(aiohttp_client, temp_dir):
    """
    Tests the full lifecycle of the HTTP server, from initialization
    to a successful and a failed tool call.
    """
    # Import here to avoid ModuleNotFoundError during test collection
    # due to the broken poetry environment in the sandbox.
    from filelist_mcp_server import handlers
    from filelist_mcp_server import http_server
    from filelist_mcp_server.exceptions import OutputFileExistsError

    # Mock the catalog creation function to avoid actual file system operations
    # and to allow us to control the outcome.
    handlers.catalog.create_catalog = AsyncMock()

    # The http_server module doesn't have a create_app function.
    # We need to create the app and add the route manually for the test.
    app = web.Application()
    app.router.add_route('POST', '/mcp', http_server.mcp_handler)
    client = await aiohttp_client(app)

    # 1. Initialize request
    init_response = await client.post("/mcp", json={
        "jsonrpc": "2.0",
        "method": "initialize",
        "params": {"capabilities": {}},
        "id": 1
    })
    init_data = await init_response.json()

    assert init_response.status == 200
    assert init_data["id"] == 1
    assert "result" in init_data
    assert "tools" in init_data["result"]["capabilities"]
    assert init_data["result"]["capabilities"]["tools"][0]["name"] == "catalog/create"

    # 2. Successful tool call
    source_dir = str(temp_dir / "source")
    output_file = str(temp_dir / "catalog.tsv")
    handlers.catalog.create_catalog.return_value = None # Simulate success

    create_response = await client.post("/mcp", json={
        "jsonrpc": "2.0",
        "method": "catalog/create",
        "params": {"target_dir": source_dir, "output_file": output_file},
        "id": 2
    })
    create_data = await create_response.json()

    assert create_response.status == 200
    assert create_data["id"] == 2
    assert create_data["result"]["status"] == "success"
    handlers.catalog.create_catalog.assert_called_once_with(source_dir, output_file)

    # 3. Failed tool call (e.g., output file exists)
    from filelist_mcp_server.exceptions import OutputFileExistsError
    handlers.catalog.create_catalog.reset_mock()
    handlers.catalog.create_catalog.side_effect = OutputFileExistsError(output_file)

    error_response = await client.post("/mcp", json={
        "jsonrpc": "2.0",
        "method": "catalog/create",
        "params": {"target_dir": source_dir, "output_file": output_file},
        "id": 3
    })
    error_data = await error_response.json()

    assert error_response.status == 200
    assert error_data["id"] == 3
    assert "error" in error_data
    assert error_data["error"]["code"] == 1001 # Custom error code for OutputFileExistsError

    # 4. Test invalid JSON
    invalid_json_response = await client.post("/mcp", data="{invalid json")
    assert invalid_json_response.status == 400
    error_data = await invalid_json_response.json()
    assert error_data["error"]["code"] == -32700 # Parse Error

    # 5. Test invalid JSON-RPC (e.g., missing 'method')
    invalid_rpc_response = await client.post("/mcp", json={"jsonrpc": "2.0", "id": 4})
    assert invalid_rpc_response.status == 200 # The server itself is fine
    error_data = await invalid_rpc_response.json()
    assert error_data["error"]["code"] == -32600 # Invalid Request
