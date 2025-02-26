from typing import Iterable
from numpy import float32
from dataclasses import dataclass
from abc import ABC, abstractmethod
from protocol.protocol import Package, Protocol

__Completion_Date = "2024_07_14_17:43"

@dataclass
class QuestionAnswerPair:
    question: str
    answer: str
    label: int

@dataclass
class Text(Protocol):
    role: str
    text: str

class UserText(Text):
    def __init__(self, text: str):
        super().__init__("user", text)


class ModelText(Text):
    def __init__(self, text: str):
        super().__init__("model", text)


def history_to_dict(historys: Iterable[Text]) -> list[dict]:
    return list({"role": h.role, "parts": [h.text]} for h in historys)

class ModelInfo(Package):
    @dataclass
    class Request(Package.Request):
        pass

    @dataclass
    class Response(Package.Response):
        model_creator_name: str
        version: str

class Predict(Package):
    @dataclass
    class Request(Package.Request):
        parts: Iterable[Text]

    @dataclass
    class Response(Package.Response):
        label_confidence: Iterable[float32]  # index = label

class ModelHandler(ABC):
    @abstractmethod
    def model_info(self) -> ModelInfo.Response:
        """
        請回傳你模型的資訊包含作者
        """
        pass

    @abstractmethod
    def invoke(self, request: Predict.Request) -> Predict.Response:
        """請你在這裡實現模型推理。
        當模型被呼叫，將收到一個`Request`，計算並給出每類的分數
        回傳強制必須是`Response`。

        備註：此function在每次使用者對話執行，非重複執行程式請在物件中新增方法。特別嚴禁止在此初始化模型。
        備註：
        """
        pass
