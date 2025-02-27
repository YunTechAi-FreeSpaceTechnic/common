import asyncio
import logging
from logging import Logger
from typing import List, Tuple
from asyncio import AbstractEventLoop

from common.protocol.byte_buffter import ByteBuffter
from common.protocol.tcp import TCPClient

from common.ModelAPI import Request, Response


class ModelBroadcaster:
    def __init__(self, logger: Logger = logging.getLogger('root')):
        self.connection_list: List[Tuple[str, int]] = []
        self.logger = logger

    def check_in(self, host: str, port: int) -> None:
        self.connection_list.append((host, port))

    def __connection_client(self,
                            addr: Tuple[str, int],
                            loop: AbstractEventLoop) -> TCPClient | None:
        try:
            self.logger.debug(f"Connecting to {addr}")
            return TCPClient(loop, addr[0], addr[1])
        except:
            self.logger.debug(f"Failed to connect to {addr}")
            return None

    def invoke(self, context: Request) -> tuple[Response, ...]:
        buf = ByteBuffter()
        context.encode(buf)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        clients = [client for addr in self.connection_list if (
            client := self.__connection_client(addr, loop))]
        tasks = [request for client in clients if (
            request := client.send(buf.to_bytes()))]
        bresponse_list = loop.run_until_complete(asyncio.gather(*tasks))

        responses = [Response.decode(ByteBuffter(data))
                     for data in bresponse_list if data is not None]

        self.logger.debug(f"Responses: {responses}")

        return tuple(responses)
