from ModelAPI import Package, Predict
from protocol.byte_buffter import ByteBuffter
from numpy import float32, array


def test_package():
    test_data = Predict.Response(
                         array([1.0, 2.0, 3.0], dtype=float32))

    buf = ByteBuffter()
    Package.encode(buf, test_data)

    test = Package.decode(buf).Response.decode(buf)

    assert (test_data.label_confidence == test.label_confidence).all()
