from common.ModelAPI import Predict, Text
from common.protocol.byte_buffter import ByteBuffter
from numpy import float32, array


def test_reponse():
    test_data = Predict.Response(array([1.0, 2.0, 3.0], dtype=float32))

    buf = ByteBuffter()
    test_data.encode(buf)
    test = Predict.Response.decode(buf)

    assert (test.label_confidence == test_data.label_confidence).all()


def test_request():
    test_data = Predict.Request([Text("user", "Hello World")])

    buf = ByteBuffter()
    test_data.encode(buf)
    test = Predict.Request.decode(buf)
    assert test_data == test
