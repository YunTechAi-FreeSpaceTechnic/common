from os import getenv
from ModelAPI import Response
import numpy as np

MINIMUM_CONFIDENCE = float(getenv("MINIMUM_CONFIDENCE") or "0.3")

def model_predict_answer(model_predict: tuple[Response, ...]) -> list[int]:
    model_prediction_label_confidence = map(lambda x: 10 ** np.argsort(list(x.label_confidence)), model_predict)
    model_prediction_result = [np.sum(t) for t in zip(*model_prediction_label_confidence)]

    return model_prediction_result[-1]
