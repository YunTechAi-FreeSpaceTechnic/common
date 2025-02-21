from ModelAPI import Response, Request, Text
from protocol.byte_buffter import ByteBuffter
from numpy import float32, array


def test_reponse():
    test_data = Response("Hello", "0912309183018301983209",
                         array([1.0, 2.0, 3.0], dtype=float32))

    buf = ByteBuffter()
    test_data.encode(buf)
    test = Response.decode(buf)

    assert test.model_creator_name == test_data.model_creator_name
    assert test.userID == test_data.userID
    assert (test.label_confidence ==
            test_data.label_confidence).all()


def test_request():
    test_data = Request("0912309183018301983209", [
                        Text("user", "Hello World")])

    buf = ByteBuffter()
    test_data.encode(buf)
    print(test_data)
    test = Request.decode(buf)
    assert test_data == test
