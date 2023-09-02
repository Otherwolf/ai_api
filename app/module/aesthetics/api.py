import inspect
import os

from .aesthetics_predictor import predict
from ..api import Api


class AestheticsScorerApi(Api):
    """
    api integration of https://github.com/kenjiqq/aesthetics-scorer
    """
    def __init__(self, model_name: str = 'sac+logos+ava1-l14-linearMSE.pth'):
        base_path = os.path.dirname(inspect.getfile(AestheticsScorerApi)).replace('\\', '/')
        self.model = predict.AestheticModel()

    def predict(self, file_path: str):
        try:
            return self.model.predict(file_path)
        except Exception as e:
            print(e)
