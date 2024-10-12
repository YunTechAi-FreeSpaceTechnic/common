import abc
from typing import Any, List, Self
from ModelAPI import Response, Request, Text
from protocol.byte_buffter import ByteBuffter
from numpy import float32


class Protocol(metaclass=abc.ABCMeta):
    data: Any

    def get_data(self):

        return self.data

    @staticmethod
    @abc.abstractmethod
    def encode(buf: ByteBuffter, data):
        pass

    @classmethod
    @abc.abstractmethod
    def decode(cls, data: ByteBuffter) -> Self:
        pass

class BString(Protocol):
    """
    Format: <length><data>
    """
    def __init__(self, data: str):
        self.data = data

    @staticmethod
    def encode(buf, data: str):
        buf.write_string(data)
    @classmethod
    def decode(cls, data: ByteBuffter):
        return cls(data.read_string())

class BFloat(Protocol):

    def __init__(self, data: float32):
        self.data = data

    @staticmethod
    def encode(buf, data: float32):
        buf.write_float(data)

    @classmethod
    def decode(cls, data: ByteBuffter):
        return cls(data.read_float())

class BFloatList(Protocol):
    def __init__(self, data: List[float32]):
        self.data = data

    @staticmethod
    def encode(buf: ByteBuffter, data: List[BFloat]):
        buf.write_int(len(data))
        for d in data:
            d.encode(buf, d.get_data())

    @classmethod
    def decode(cls, data: ByteBuffter):
        data_list = []
        list_size = data.read_int()

        for _ in range(list_size):
            data_list.append(BFloat.decode(data).get_data())

        return BFloatList(data_list)

class BText(Protocol):
    def __init__(self, data: Text):
        self.data = data
    @staticmethod
    def encode(buf: ByteBuffter, data: Text):
        BString.encode(buf, data.role)
        BString.encode(buf, data.text)
    @classmethod
    def decode(cls, data: ByteBuffter):
        role = BString.decode(data).get_data()
        text = BString.decode(data).get_data()

        return BText(Text(role, text))

class BTextList(Protocol):
    def __init__(self, data: List[Text]):
        self.data = data
    @staticmethod
    def encode(buf: ByteBuffter, data: List[BText]):
        buf.write_int(len(data))
        for d in data:
            d.encode(buf, d.get_data())
    @classmethod
    def decode(cls, data: ByteBuffter):
        data_list = []
        list_size = data.read_int()
        for _ in range(list_size):
            data_list.append(BText.decode(data).get_data())
        return BTextList(data_list)

class BResponse(Protocol):
    def __init__(self, data: Response):
        self.data = data

    @staticmethod
    def encode(buf: ByteBuffter, data: Response):
        buf.write_string(data.model_creator_name)
        buf.write_string(data.userID)
        b_float_map = map(lambda x: BFloat(x), data.label_confidence)
        BFloatList.encode(buf, list(b_float_map))

    @classmethod
    def decode(cls, data: ByteBuffter):
        model_creator_name = BString.decode(data).get_data()
        userID = BString.decode(data).get_data()
        label_confidence = BFloatList.decode(data).get_data()

        return BResponse(Response(model_creator_name, userID, label_confidence))

class BRequest(Protocol):
    def __init__(self, data: Request):
        self.data = data
    @staticmethod
    def encode(buf: ByteBuffter, data: Request):
        buf.write_string(data.userID)

        BTextList.encode(buf, list(map(lambda x: BText(x), data.parts)))
    @classmethod
    def decode(cls, data: ByteBuffter):
        userID = BString.decode(data).get_data()
        parts = BTextList.decode(data).get_data()
        return BRequest(Request(userID, parts))
