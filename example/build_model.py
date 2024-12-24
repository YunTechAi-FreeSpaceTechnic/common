from common.ModelAPI import ModelHandler, Response, Request


# 必須實作ModelHandler 並且實作invoke方法
class ExampleModel(ModelHandler):
    def __init__(self): # 這裡放模型初始化的程式碼
        ...

    def invoke(self, request: Request) -> Response:  # 這裡放模型推理的程式碼
        # request 的結構:
        # request = Request(userID: str, parts: List[Text(role: str, content: str)])
        # request.userID = 使用者ID，需要再response中回傳
        # request.parts = 對話歷史list，每個對話是一個Text物件
        # request.parts[0].role = 對話者，"user" 或 "model" 或其他
        # request.parts[0].content = 對話內容
        
        # 如果模型無法處裡歷史訊息，請合併所有對話，或是只取最後一個對話
                
        result = [] # 這裡放模型推理的結果
        # result 需要是 Iterable[float32]
        # 它應該要長這樣的: 
        # result = [0.1, 0.2, 0.3, 0.4, 0.5, ...]
        # len(result) = 類別數 (不包含空類別，空類別請用[0, 0, 0, ...]表示)
        
        return Response("your_name", request.userID, result)


# ModelServer 會呼叫setup() 來取得ModelHandler物件
def setup() -> ModelHandler:
    return ExampleModel() # 請在這裡回傳你的ModelHandler物件
