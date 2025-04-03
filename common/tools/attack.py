import asyncio
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from common.protocol.tcp import TCPClient
from common.protocol.protocol import Package, ByteBuffter
from common.ModelAPI import ModelInfo, Error as ModelError, Predict, Text

async def attack(host: str, port: int):
    client = TCPClient(host, port)

    await client.connection()

    while True:
        fn = input("Function: ")

        if fn == "info":
            print(await info(client))
        elif fn == "predict":
            print(await predict(client))

async def info(client: TCPClient):
    buf = ByteBuffter()
    Package.encode(buf, ModelInfo.Request())
    data = await client.send(buf.to_bytes()) or bytearray()
    response_buf = ByteBuffter(bytes(data))
    check_error(Package.decode(response_buf), response_buf)
    model_info = ModelInfo.Response.decode(response_buf)

    return model_info

async def predict(client:TCPClient):
    buf = ByteBuffter()
    text = input("Input text:")
    Package.encode(buf, Predict.Request([
        Text("User", text)
    ]))
    data = await client.send(buf.to_bytes()) or bytearray()
    response_buf = ByteBuffter(bytes(data))

    check_error(Package.decode(response_buf), response_buf)
    predict = Predict.Response.decode(response_buf)

    return predict

def check_error(package: type[Package], buf: ByteBuffter):
    if package == ModelError:
        model_error = ModelError.Response.decode(buf)
        print(model_error.message)

        raise Exception(model_error.message)
    else:
        return package

def main():
    host = sys.argv[1]
    port = int(sys.argv[2])

    asyncio.run(attack(host, port))

if __name__ == "__main__":
    main()
