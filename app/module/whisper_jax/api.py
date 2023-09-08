"""
faster-whisper is a reimplementation of OpenAI's Whisper model using CTranslate2,
 which is a fast inference engine for Transformer models.

This implementation is up to 4 times faster than openai/whisper for the same accuracy while using less memory.
The efficiency can be further improved with 8-bit quantization on both CPU and GPU.

"""
from typing import Optional, BinaryIO

import torch
import whisper

from app.module.api import Api


class WhisperApi(Api):
    """
    api integration of https://github.com/guillaumekln/faster-whisper
    """
    def __init__(self, model_name: str = 'small'):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = whisper.load_model(model_name).to(self.device)

    def recognize(self, file_bytes: bytes, language: Optional[str]):
        try:
            with torch.cuda.device(self.device):
                return self.model.transcribe(file_bytes, language=language)
        except Exception as e:
            print(e)

    def __str__(self):
        return f'WhisperApi[{self.device}]'
