from app.module.api import Api
from .classificator import model


class ClassificatorApi(Api):
    def __init__(self):
        self.model = model.ClassificatorModel()

    def predict(self, file_path: str, labels: list):
        try:
            return self.model.predict(file_path, labels)
        except Exception as e:
            print(e)

    def __str__(self):
        return f"ClassificatorApi[{self.model.device}]"
