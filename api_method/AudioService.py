import time

from app.module.BaseApi import BaseApi


class AudioService(BaseApi):
    async def stt(self, audio, language: str):
        if language == 'auto':
            language = None

        t = time.time()
        segments = await self.whisper.recognize(audio, language)
        print('step: ', time.time() - t)
        return segments['text'].strip(), None
