from typing import Self, Any, get_args
from collections.abc import Iterable
import inspect
from protocol.byte_buffter import ByteBuffter
from numpy import float32, ndarray


class Protocol():
    def encode(self, buf: ByteBuffter):
        '''
        # Usage Example:
        >>> @dataclass
        >>> class DataA:
        >>>    a: str
        >>>    b: str
        >>>
        >>> buf = ByteBuffter()
        >>> DataA("abc", "abc").encode(buf)
        '''
        for d in self.__dict__.values():
            self.builtin_encode(buf, d)

    def builtin_encode(self, buf: ByteBuffter, data: Any):
        t = type(data)

        if t == list or t == ndarray:
            buf.write_int(len(data))
            for a in data:
                self.builtin_encode(buf, a)
        elif t == int:
            buf.write_int(data)
        elif t == float or t == float32:
            buf.write_float(data)
        elif t == str:
            buf.write_string(data)
        elif issubclass(t, Protocol):
            data.encode(buf)

    @classmethod
    def decode(cls, data: ByteBuffter) -> Self:
        '''
        # Usage Example:
        >>> @dataclass
        >>> class DataA:
        >>>    a: str
        >>>    b: str
        >>>
        >>> buf = ByteBuffter()
        >>> a = DataA.decode(buf)
        '''
        args = []
        for name, param in inspect.signature(cls.__init__).parameters.items():
            if name != "self":
                t = param.annotation

                args.append(cls.builtin_decode(t, data))

        return cls(*args)

    @staticmethod
    def builtin_decode(t: Any, data: ByteBuffter) -> Any:
        if t == list or t == ndarray or isinstance(t, Iterable):
            size = data.read_int()
            return [Protocol.builtin_decode(
                get_args(t)[0], data
            ) for i in range(size)]
        elif t == int:
            return data.read_int()
        elif t == float or t == float32:
            return data.read_float()
        elif t == str:
            return data.read_string()
        elif issubclass(t, Protocol):
            return t.decode(data)
