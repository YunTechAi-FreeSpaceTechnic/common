from common.broadcaster import ModelBroadcaster
from common.ModelAPI import Request, Text
import numpy as np
import logging

# --- -- - -- --- 初始化 --- -- - -- ---
# 範例log
logger = logging.getLogger('example logger')
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)s in %(module)s: %(message)s'))
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

mm = ModelBroadcaster(logger)  # 使用自訂logger進行初始化
# mm = ModelBroadcaster()  # 如果不設定logger，則使用root logger

# 加入模型伺服器
mm.check_in('localhost', 6666)
mm.check_in('localhost', 6667)
mm.check_in('localhost', 6668)
# mm.check_in('host', port)

# --- -- - -- --- 使用 --- -- - -- ---
# 建立一個聊天歷史的請求
history = [
    Text("user", "您好我有問題"),
    Text("model", "請問您的問題是什麼呢？"),
    Text("user", "我想問一下電梯會如何應對地震"),
    # Text("誰", "內容"),
]
request = Request("123456789", history)
# Request("userID", 聊天歷史)

# 呼叫模型
response = mm.invoke(request)
# response 是 tuple[Response, ...]

# 如果response 是空的，代表沒有模型回應
if len(response) == 0:
    logger.error("No model response received.")
    raise Exception("No model response received.")

# 範例  印出模型回應的資訊
for res in response:
    print(f"Model Creator: {res.model_creator_name}")  # 顯示模型創建者
    print(f"User ID: {res.userID}")  # 顯示userID
    print(f"Label Confidence: {res.label_confidence}")  # 顯示每類的分數
    print()

# 範例  使用sum計算出最高分的類別
label_confidence = [re.label_confidence for re in response]  # 取出label_confidence
mix_label_confidence = np.sum(label_confidence, axis=0)  # 對0軸做sum
max_index = np.argmax(mix_label_confidence)  # 取出最大值的index
print(f"Max confidence label index: {max_index}")  # 顯示最高分的類別
