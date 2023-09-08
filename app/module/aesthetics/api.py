"""
Predicts aesthetic scores for images. Trained on AI Horde community ratings of Stable Diffusion generated images.
"""
import inspect
import os
from typing import Optional

from .aesthetics_predictor import predict
from ..api import Api


class AestheticsScorerApi(Api):
    """
    api integration of https://github.com/kenjiqq/aesthetics-scorer
    """
    def __init__(self, device: Optional[str], model_name: str = predict.DEFAULT_MODEL_NAME):
        base_path = os.path.dirname(inspect.getfile(AestheticsScorerApi)).replace('\\', '/')
        self.model = predict.AestheticModel(device, model_name)

    def predict(self, file_path: str):
        try:
            return self.model.predict(file_path)
        except Exception as e:
            print(e)

    def __str__(self):
        return f'AestheticsScorerApi[{self.model.device}]'
