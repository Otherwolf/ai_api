"""
Trained on 60+ Gigs of data to identify:

drawings - safe for work drawings (including anime)
hentai - hentai and pornographic drawings
neutral - safe for work neutral images
porn - pornographic images, sexual acts
sexy - sexually explicit images, not pornography
This model powers NSFW JS - More Info
"""
import inspect
import os

from app.module.api import Api
from .nsfw_detector import predict
from ...helper import load_model


class NSFWDetectorApi(Api):
    """
    api integration of https://github.com/GantMan/nsfw_model
    """
    def __init__(self, nsfw_model: str = 'nsfw.299x299', size: int = 299):
        base_path = os.path.dirname(inspect.getfile(NSFWDetectorApi)).replace('\\', '/')
        nsfw_path_model = f'{base_path}/nsfw_detector/{nsfw_model}.h5'
        load_model(nsfw_path_model, "https://s3.amazonaws.com/ir_public/ai/nsfw_models/february_2019_nsfw.299x299.h5")
        self.model = predict.Predictor(f'{base_path}/nsfw_detector/{nsfw_model}.h5', size)

    def predict(self, file_path: str):
        try:
            return self.model.classify(file_path)[0]
        except Exception as e:
            print(e)

    def __str__(self):
        return f'NSFWDetectorApi[{self.model.device}]'
