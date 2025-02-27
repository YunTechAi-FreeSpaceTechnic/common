import struct
from numpy import float32


class ByteBuffter():
    def __init__(self, data: bytes = bytes()):
        self.data = data
        self.index = 0
        self.length = len(data)

    def read(self, size: int) -> bytes:
        if self.index + size > self.length:
            raise IndexError("Out of range")
        data = self.data[self.index:self.index + size]
        self.index += size
        return data

    def read_byte(self) -> int:
        return int.from_bytes(self.read(1), 'big')

    def read_int(self) -> int:
        return int.from_bytes(self.read(4), 'big')

    def read_float(self) -> float32:
        [value] = struct.unpack('f', self.read(4))

        return float32(value)

    def read_string(self) -> str:
        length = self.read_int()
        return self.read(length).decode()

    def write(self, data: bytes):
        self.data += data
        self.length += len(data)

    def write_byte(self, data: int):
        self.write(data.to_bytes(1, 'big'))

    def write_int(self, data: int):
        self.write(data.to_bytes(4, 'big'))

    def write_float(self, data: float32):
        self.write(struct.pack('f', data))

    def write_string(self, data: str):
        data_bytes = data.encode()
        self.write_int(len(data_bytes))
        self.write(data_bytes)

    def to_bytes(self) -> bytes:
        return self.data
