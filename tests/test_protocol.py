from ModelAPI import Response, Request, Text
from protocol.byte_buffter import ByteBuffter
from protocol.protocol import BString, BResponse, BRequest
from numpy import float32, array

def test_string():
    test_str = "Test String: Hello World"
    buf = ByteBuffter()
    BString.encode(buf, test_str)
    test = BString.decode(buf)

    assert test.get_data() == test_str

def test_reponse():
    test_data = Response("Hello", "0912309183018301983209", array([1.0, 2.0, 3.0], dtype=float32))

    buf = ByteBuffter()
    BResponse.encode(buf, test_data)
    test = BResponse.decode(buf)

    assert test.get_data().model_creator_name == test_data.model_creator_name
    assert test.get_data().userID == test_data.userID
    assert (test.get_data().label_confidence == test_data.label_confidence).all()


def test_request():
    test_data = Request("0912309183018301983209", [Text("user", "Hello World")])

    buf = ByteBuffter()
    BRequest.encode(buf, test_data)
    test = BRequest.decode(buf)
    assert test_data == test.get_data()
