import os
import traceback

from os import listdir
from os.path import isfile, join, exists, isdir, abspath
from typing import List, Union, Tuple, Any, Optional

import numpy as np
import tensorflow as tf
from numpy import ndarray
from tensorflow import keras
import tensorflow_hub as hub


os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

DEFAULT_MODEL_NAME = 'nsfw.299x299'
DOWNLOAD_DEFAULT_MODEL_LINK = "https://s3.amazonaws.com/ir_public/ai/nsfw_models/february_2019_nsfw.299x299.h5"


class Predictor:
    def __init__(self, device: Optional[str], model_path: str = DEFAULT_MODEL_NAME, image_dim: int = 299):
        self.image_dim = image_dim

        if (physical_devices := tf.config.list_physical_devices('GPU')) and device != 'cpu':
            tf.config.experimental.set_memory_growth(physical_devices[0], True)
            self.device = '/GPU:0'

        elif device != 'gpu':
            self.device = '/CPU:0'

        if not hasattr(self, 'device'):
            raise Exception('The model NSFW detector doesn`t have device option')

        with tf.device(self.device):
            self.model = tf.keras.models.load_model(model_path, custom_objects={
                'KerasLayer': hub.KerasLayer})

    def classify(self, input_paths: Union[str, List[str]]) -> dict:
        """ Classify given a model, input paths (could be single string), and image dimensionality...."""
        images, image_paths = self.load_images(input_paths)
        probs = self._classify_nd(images)
        return probs

    def load_images(self, image_paths: Union[str, List[str]], verbose: bool = False)\
            -> Tuple[ndarray, List[str]]:
        '''
        Function for loading images into numpy arrays for passing to model.predict
        inputs:
            image_paths: list of image paths to load
            image_size: size into which images should be resized
            verbose: show all of the image path and sizes loaded
        outputs:
            loaded_images: loaded images on which keras model can run predictions
            loaded_image_paths: paths of images which the function is able to process
        '''
        loaded_images = []
        loaded_image_paths = []
        image_size = (self.image_dim, self.image_dim)

        if isdir(image_paths):
            parent = abspath(image_paths)
            image_paths = [join(parent, f) for f in listdir(
                image_paths) if isfile(join(parent, f))]
        elif isfile(image_paths):
            image_paths = [image_paths]

        for img_path in image_paths:
            try:
                if verbose:
                    print(img_path, "size:", image_size)
                image = keras.preprocessing.image.load_img(
                    img_path, target_size=image_size)
                image = keras.preprocessing.image.img_to_array(image)
                image /= 255
                loaded_images.append(image)
                loaded_image_paths.append(img_path)
            except Exception as ex:
                print("Image Load Failure: ", img_path, ex)
                print(traceback.format_exc())

        return np.asarray(loaded_images), loaded_image_paths

    def _classify_nd(self, nd_images: ndarray) -> List[dict]:
        """ Classify given a model, image array (numpy)...."""

        with tf.device(self.device):
            model_preds = self.model.predict(nd_images)

        categories = ['drawings', 'hentai', 'neutral', 'porn', 'sexy']

        probs = []
        for i, single_preds in enumerate(model_preds):
            single_probs = {}
            for j, pred in enumerate(single_preds):
                single_probs[categories[j]] = round(float(pred), 6) * 100
            probs.append(single_probs)
        return probs
