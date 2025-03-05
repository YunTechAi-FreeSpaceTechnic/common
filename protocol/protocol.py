from abc import ABC, abstractmethod
from typing import Self, Any, get_args
from collections.abc import Iterable
import inspect
from common.protocol.byte_buffter import ByteBuffter
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
        for k, d in self.__dict__.items():
            if k == "id":
                buf.write_byte(d)
            else:
                self.builtin_encode(buf, d)

    def builtin_encode(self, buf: ByteBuffter, data: Any):
        t = type(data)

        if t == list or t == ndarray or t == tuple:
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
            if name == "id":
                args.append(data.read_byte())
            elif name != "self":
                t = param.annotation

                args.append(cls.builtin_decode(t, data))

        return cls(*args)

    @staticmethod
    def builtin_decode(t: Any, data: ByteBuffter) -> Any:
        if t == list or t == ndarray or isinstance(t, Iterable) or t == tuple:
            size = data.read_int()
            return [Protocol.builtin_decode(
                get_args(t)[0], data
            ) for _ in range(size)]
        elif t == int:
            return data.read_int()
        elif t == float or t == float32:
            return data.read_float()
        elif t == str:
            return data.read_string()
        elif issubclass(t, Protocol):
            return t.decode(data)

@abstractmethod
class Package:
    class Request(ABC, Protocol):
        pass

    class Response(ABC, Protocol):
        pass

    @classmethod
    def decode(cls, data: ByteBuffter):
        subclass = cls.__subclasses__()
        id = data.read_byte()

        return subclass[id]

    @classmethod
    def encode(cls, buf: ByteBuffter, data: Protocol):
        for index, subclass in enumerate(cls.__subclasses__()):
            if type(data) in [cls for _, cls in inspect.getmembers(subclass) if inspect.isclass(cls)]:
                buf.write_byte(index)

        data.encode(buf)

