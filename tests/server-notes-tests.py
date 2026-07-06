# test_server.py
import pytest
from fastmcp import Client
from mcp_server.server_notes import mcp  # Import the mcp object, not mcp.run()


@pytest.mark.asyncio
async def test_list_notes_when_empty():
    async with Client(mcp) as client:
        result = await client.call_tool("list_notes", {})
        assert "No notes saved yet" in result.content[0].text


@pytest.mark.asyncio
async def test_add_and_retrieve_note():
    async with Client(mcp) as client:
        # Add a note
        result = await client.call_tool(
            "add_note", {"name": "meeting-notes", "content": "Discussed Q2 roadmap"}
        )
        assert "added successfully" in result.content[0].text

        # Retrieve it
        result = await client.call_tool("get_note", {"name": "meeting-notes"})
        assert result.content[0].text == "Discussed Q2 roadmap"


@pytest.mark.asyncio
async def test_delete_note():
    async with Client(mcp) as client:
        await client.call_tool("add_note", {"name": "temp", "content": "delete me"})
        result = await client.call_tool("delete_note", {"name": "temp"})
        assert "deleted" in result.content[0].text

        # Verify it's gone
        result = await client.call_tool("get_note", {"name": "temp"})
        assert "not found" in result.content[0].text


@pytest.mark.asyncio
async def test_get_nonexistent_note():
    async with Client(mcp) as client:
        result = await client.call_tool("get_note", {"name": "ghost-note"})
        assert "not found" in result.content[0].text


@pytest.mark.asyncio
async def test_resources_are_accessible():
    async with Client(mcp) as client:
        # Read the count resource
        resources = await client.list_resources()
        resource_uris = [str(r.uri) for r in resources]
        assert any("notes://" in uri for uri in resource_uris)
