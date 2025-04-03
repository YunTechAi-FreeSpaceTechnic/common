import importlib.resources
import json

def load_labels():
    json_str = importlib.resources.read_text("common.data", "2024業務常見問題.json")

    return json.loads(json_str)
