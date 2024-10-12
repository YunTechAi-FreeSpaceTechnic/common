from os import getenv
from ModelAPI import Response
import numpy as np

MINIMUM_CONFIDENCE = float(getenv("MINIMUM_CONFIDENCE") or "0.3")

def model_predict_answer(model_predict: tuple[Response, ...]) -> list[int]:
    model_prediction_label_confidence = map(lambda x: x.label_confidence, model_predict)
    model_prediction_result = [np.sum(t)/len(model_predict) for t in zip(*model_prediction_label_confidence)]
    model_prediction_reply = list(map(
        lambda x: x[0],
        filter(
            lambda x: x[1] > MINIMUM_CONFIDENCE,
            enumerate(model_prediction_result)
        )
    ))

    return model_prediction_reply
