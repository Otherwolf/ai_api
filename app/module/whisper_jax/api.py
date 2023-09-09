"""
faster-whisper is a reimplementation of OpenAI's Whisper model using CTranslate2,
 which is a fast inference engine for Transformer models.

This implementation is up to 4 times faster than openai/whisper for the same accuracy while using less memory.
The efficiency can be further improved with 8-bit quantization on both CPU and GPU.

"""
import io
from typing import Optional, BinaryIO

import torch
from faster_whisper import WhisperModel

from app.module.api import Api


class WhisperApi(Api):
    """
    api integration of https://github.com/guillaumekln/faster-whisper
    """
    def __init__(self, device: Optional[str], model_name: str = 'small'):
        self.device = device or 'cuda'
        self.model = WhisperModel(model_name, device=self.device)

    def recognize(self, file_bytes: io.BytesIO, language: Optional[str]):
        try:
            return self.model.transcribe(file_bytes, beam_size=5, language=language)
        except Exception as e:
            print(e)

    def __str__(self):
        return f'WhisperApi[{self.device}]'
