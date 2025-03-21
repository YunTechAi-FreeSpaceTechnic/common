import asyncio
from concurrent.futures import ThreadPoolExecutor
from collections.abc import Callable
from asyncio import Server, StreamReader, StreamWriter
from logging import Logger

SOCKET_BUFFET_SIZE = 8192


class TCPServer():

    def __init__(self,
                 logger: Logger,
                 host: str = "0.0.0.0",
                 port=6666,
                 callback: Callable[[bytearray], bytearray] = lambda x: x):
        self.port = port
        self.host = host
        self.callback = callback
        self.logger = logger

    async def server(self, executor: ThreadPoolExecutor):
        return await asyncio.start_server(
            Connection(self.logger, executor, self.callback).listen, self.host,
            self.port)

    async def listen(self, server: Server | None = None, max_workers: int = 5):
        with ThreadPoolExecutor(max_workers) as executor:
            server = server or await self.server(executor)
            self.logger.info("Listening for connections...")

            await server.serve_forever()

class Connection():

    def __init__(self, logger: Logger, executor: ThreadPoolExecutor, callback: Callable[[bytearray],
                                                          bytearray]):
        self.logger = logger
        self.callback = callback
        self.executor = executor
        self.loop = asyncio.get_running_loop()

    async def send(self, data):
        size = len(data)

        self.writer.write(size.to_bytes(4))
        self.writer.write(data)

        await self.writer.drain()

    async def recv(self):
        buf_bytes = bytearray()
        size = await self.reader.read(4)
        self.logger.debug(f"Server received size: {size}")

        if not size:
            return None
        size = int.from_bytes(size)

        for _ in range(int(size / SOCKET_BUFFET_SIZE)):
            buf_bytes.extend(await self.reader.read(SOCKET_BUFFET_SIZE))

        buf_bytes.extend(await self.reader.read(size % SOCKET_BUFFET_SIZE))

        return buf_bytes

    async def listen(self, reader: StreamReader, writer: StreamWriter):
        self.reader = reader
        self.writer = writer
        self.peername = writer.get_extra_info('peername')

        try:
            while True:
                data = await self.recv()

                if not data:
                    break

                self.logger.debug(f"Server received data: {data}")
                response = await self.loop.run_in_executor(self.executor, self.callback, data)

                await self.send(response)
        finally:
            self.close()

    def close(self):
        self.logger.info(f"Connection from {self.peername} closed.")


class TCPClient():

    def __init__(self, host="localhost", port=6666):
        self.host = host
        self.port = port

    async def connection(self):
        self.reader, self.writer = await asyncio.open_connection(
            self.host, self.port)

    async def send(self, data: bytes) -> bytearray | None:
        size = len(data)
        self.writer.write(size.to_bytes(4) + data)

        await self.writer.drain()

        return await self.recv()

    async def recv(self):
        size = await self.reader.read(4)
        buf_bytes = bytearray()

        if not size:
            return None

        size = int.from_bytes(size)

        for _ in range(int(size / SOCKET_BUFFET_SIZE)):
            buf_bytes.extend(await self.reader.read(SOCKET_BUFFET_SIZE))

        buf_bytes.extend(await self.reader.read(SOCKET_BUFFET_SIZE))

        return buf_bytes

    def close(self):
        self.writer.close()
