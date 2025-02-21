from protocol.tcp import TCPServer, TCPClient
import pytest
import asyncio
import logging

pytest_plugins = ('pytest_asyncio',)


@pytest.mark.asyncio
async def test_tcp_server():
    test_data = b"Hello World"
    server = TCPServer(logging)
    server.listen_thread.start()
    await asyncio.sleep(1)
    client = TCPClient(asyncio.get_event_loop())
    data = await client.send(test_data)

    assert data == test_data
