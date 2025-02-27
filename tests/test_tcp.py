from common.protocol.tcp import TCPServer, TCPClient
from common.protocol.byte_buffter import ByteBuffter
from common.ModelAPI import Predict, Text
import pytest
import asyncio
import logging

pytest_plugins = ('pytest_asyncio',)


@pytest.mark.asyncio
async def test_tcp_server():
    test_data = Predict.Request([Text("ab", "") for i in range(10000)])
    buf = ByteBuffter()
    test_data.encode(buf)
    server = TCPServer(logging)
    server.listen_thread.start()

    await asyncio.sleep(1)

    client = TCPClient(asyncio.get_event_loop())
    data = await client.send(buf.to_bytes())

    assert Predict.Request.decode(ByteBuffter(data)) == test_data
