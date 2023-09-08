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
from typing import Optional

from app.module.api import Api
from .nsfw_detector import predict
from ...helper import load_model


class NSFWDetectorApi(Api):
    """
    api integration of https://github.com/GantMan/nsfw_model
    """
    def __init__(self, device: Optional[str], nsfw_model: str = predict.DEFAULT_MODEL_NAME, size: int = 299):

        # getting model path
        base_path = os.path.dirname(inspect.getfile(NSFWDetectorApi)).replace('\\', '/')
        nsfw_path_model = f'{base_path}/nsfw_detector/{nsfw_model}.h5'

        # download if model doesnt exist
        load_model(nsfw_path_model, predict.DOWNLOAD_DEFAULT_MODEL_LINK)

        # load model
        self.model = predict.Predictor(device, nsfw_path_model, size)

    def predict(self, file_path: str):
        try:
            return self.model.classify(file_path)[0]
        except Exception as e:
            print(e)

    def __str__(self):
        return f'NSFWDetectorApi[{self.model.device}]'
