from common.protocol.tcp import TCPServer, TCPClient
from common.protocol.byte_buffter import ByteBuffter
from common.ModelAPI import Predict, Text
import pytest
import asyncio
import logging
import threading

pytest_plugins = ('pytest_asyncio', )


@pytest.mark.asyncio
async def test_tcp_server():
    test_data = Predict.Request([Text("ab", "") for _ in range(10000)])
    buf = ByteBuffter()
    test_data.encode(buf)
    tcp_server = TCPServer(logging.Logger("Test"))
    server_task = asyncio.create_task(tcp_server.listen())

    client = TCPClient()
    await client.connection()
    data = await client.send(buf.to_bytes())

    client.close()
    tcp_server.close()
    server_task.cancel()

    assert Predict.Request.decode(ByteBuffter(data)) == test_data
