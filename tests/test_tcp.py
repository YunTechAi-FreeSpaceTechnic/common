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
    server = TCPServer(logging.Logger("Test"))
    server_thread = threading.Thread(target=server.listen)

    server_thread.start()

    client = TCPClient(asyncio.get_event_loop())
    data = await client.send(buf.to_bytes())

    client.close()
    server.close()

    assert Predict.Request.decode(ByteBuffter(data)) == test_data
