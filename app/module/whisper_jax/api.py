"""
faster-whisper is a reimplementation of OpenAI's Whisper model using CTranslate2,
 which is a fast inference engine for Transformer models.

This implementation is up to 4 times faster than openai/whisper for the same accuracy while using less memory.
The efficiency can be further improved with 8-bit quantization on both CPU and GPU.

"""
from typing import Optional, BinaryIO

import tensorflow as tf
from whisper_jax import FlaxWhisperPipline

from app.module.api import Api


OMP_NUM_THREADS = 8


class WhisperApi(Api):
    """
    api integration of https://github.com/guillaumekln/faster-whisper
    """
    def __init__(self, model_name: str = 'openai/whisper-small'):
        self.device = 'cuda' if tf.config.list_physical_devices('GPU') else 'cpu'
        self.pipeline = FlaxWhisperPipline(model_name)

    def recognize(self, file_bytes: bytes, language: Optional[str]):
        try:
            return self.pipeline(file_bytes, language=language)
        except Exception as e:
            print(e)

    def __str__(self):
        return f'WhisperApi[{self.device}]'
