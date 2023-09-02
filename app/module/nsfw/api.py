import inspect
import os

from app.module.api import Api
from .nsfw_detector import predict


class NSFWDetectorApi(Api):
    """
    api integration of https://github.com/GantMan/nsfw_model
    """
    def __init__(self, nsfw_model: str = 'nsfw.299x299', size: int = 299):
        base_path = os.path.dirname(inspect.getfile(NSFWDetectorApi)).replace('\\', '/')
        self.image_dim = size
        self.model = predict.load_model(f'{base_path}/nsfw_detector/{nsfw_model}.h5')

    def predict(self, file_path: str):
        try:
            return predict.classify(self.model, file_path, self.image_dim)[0]
        except Exception as e:
            print(e)
