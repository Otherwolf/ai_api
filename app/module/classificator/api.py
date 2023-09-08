from typing import Optional

from app.module.api import Api
from .classificator import model


class ClassificatorApi(Api):
    def __init__(self, device: Optional[str], model_name: str = model.DEFAULT_MODEL_NAME):
        self.model = model.ClassificatorModel(device, model_name)

    def predict(self, file_path: str, labels: list):
        try:
            return self.model.predict(file_path, labels)
        except Exception as e:
            print(e)

    def __str__(self):
        return f"ClassificatorApi[{self.model.device}]"
