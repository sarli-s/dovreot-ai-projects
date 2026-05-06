"""
Tests for the MCP + Gemini project.
- MCP clients / tools: tested for real (no network needed).
- Gemini API calls: mocked (blocked by NetFree).
"""
import os
import pytest
import pytest_asyncio
from unittest.mock import MagicMock, patch, AsyncMock
from google.genai import types


# ── helpers ──────────────────────────────────────────────────────────────────

def make_gemini_text_response(text: str):
    """Fake Gemini response with a real types.Part so Pydantic accepts it."""
    part = types.Part(text=text)
    candidate = MagicMock()
    candidate.content.parts = [part]
    response = MagicMock()
    response.candidates = [candidate]
    return response


def make_gemini_tool_response(tool_name: str, args: dict):
    """Fake Gemini response that requests a tool call."""
    part = types.Part.from_function_call(name=tool_name, args=args)
    candidate = MagicMock()
    candidate.content.parts = [part]
    response = MagicMock()
    response.candidates = [candidate]
    return response


# ── fixtures ──────────────────────────────────────────────────────────────────

@pytest_asyncio.fixture
async def host():
    with patch.dict(os.environ, {"GEMINI_API_KEY": "fake-key"}):
        with patch("host.genai.Client"):
            from host import ChatHost
            h = ChatHost()
            yield h
            # Don't call h.cleanup() here — anyio cancel scopes can't be
            # closed from a different task than they were opened in.


# ── MCP connectivity tests (real subprocesses) ───────────────────────────────

@pytest.mark.asyncio
async def test_mcp_usa_connects_and_exposes_tools():
    from client import MCPClient
    client = MCPClient("./weather_USA.py")
    try:
        await client.connect_to_server()
        assert client.session is not None
        response = await client.session.list_tools()
        tool_names = [t.name for t in response.tools]
        assert "get_alerts_in_USA" in tool_names
        assert "get_forecast_in_USA" in tool_names
    finally:
        await client.cleanup()


@pytest.mark.asyncio
async def test_mcp_israel_connects_and_exposes_tools():
    from client import MCPClient
    client = MCPClient("./weather_Israel.py")
    try:
        await client.connect_to_server()
        assert client.session is not None
        response = await client.session.list_tools()
        tool_names = [t.name for t in response.tools]
        assert "open_weather_forecast_israel" in tool_names
        assert "enter_weather_forecast_city_israel" in tool_names
        assert "select_weather_forecast_city_israel" in tool_names
    finally:
        await client.cleanup()


# ── ChatHost unit tests (Gemini mocked) ──────────────────────────────────────

@pytest.mark.asyncio
async def test_get_available_tools_structure(host):
    await host.connect_mcp_clients()
    tools = await host.get_available_tools()

    assert len(tools) > 0
    for t in tools:
        assert "name" in t
        assert "description" in t
        assert "parameters" in t
        assert "__" in t["name"]


@pytest.mark.asyncio
async def test_tool_clients_populated_after_get_tools(host):
    await host.connect_mcp_clients()
    tools = await host.get_available_tools()

    for t in tools:
        assert t["name"] in host.tool_clients
        client, original = host.tool_clients[t["name"]]
        assert original in t["name"]


@pytest.mark.asyncio
async def test_process_query_no_tool_call(host):
    await host.connect_mcp_clients()
    await host.get_available_tools()

    host.client.models.generate_content = MagicMock(
        return_value=make_gemini_text_response("The weather is sunny.")
    )

    result = await host.process_query("What is the weather?")
    assert "sunny" in result


@pytest.mark.asyncio
async def test_process_query_with_tool_call(host):
    await host.connect_mcp_clients()
    await host.get_available_tools()

    exposed_name = next(iter(host.tool_clients))
    mcp_client, original_name = host.tool_clients[exposed_name]

    tool_result_part = MagicMock()
    tool_result_part.text = "Sunny, 25°C"
    tool_result = MagicMock()
    tool_result.content = [tool_result_part]
    mcp_client.session.call_tool = AsyncMock(return_value=tool_result)

    host.client.models.generate_content = MagicMock(side_effect=[
        make_gemini_tool_response(exposed_name, {}),
        make_gemini_text_response("It is sunny and 25°C."),
    ])

    result = await host.process_query("What is the weather?")
    assert "25" in result
    mcp_client.session.call_tool.assert_called_once_with(original_name, {})


@pytest.mark.asyncio
async def test_missing_api_key_raises():
    env = {k: v for k, v in os.environ.items() if k != "GEMINI_API_KEY"}
    with patch.dict(os.environ, env, clear=True):
        with patch("host.genai.Client"):
            from host import ChatHost
            with pytest.raises(ValueError, match="GEMINI_API_KEY"):
                ChatHost()


# ── visual / integration test (opens real browser) ───────────────────────────

@pytest.mark.asyncio
async def test_israel_weather_browser_opens_and_searches():
    """
    Real end-to-end test for weather_Israel.py:
    opens the website, types a city, and selects it from the dropdown.
    You will SEE the browser open and the city typed in the search box.
    """
    from client import MCPClient
    client = MCPClient("./weather_Israel.py")
    try:
        await client.connect_to_server()

        result = await client.session.call_tool("open_weather_forecast_israel", {})
        assert "נפתח" in str(result.content)

        result = await client.session.call_tool(
            "enter_weather_forecast_city_israel", {"city": "ירושלים"}
        )
        assert "ירושלים" in str(result.content)

        result = await client.session.call_tool("select_weather_forecast_city_israel", {})
        assert "נבחרה" in str(result.content)

    finally:
        await client.cleanup()
