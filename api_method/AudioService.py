import time

from app.module.BaseApi import BaseApi


class AudioService(BaseApi):
    async def stt(self, audio, language: str):
        audio_bytes = await audio.read()
        if language == 'auto':
            language = None

        t = time.time()
        text = await self.whisper.recognize(audio_bytes, language)
        print(text)
        print('step: ', time.time() - t)
        return text['text'].strip(), None
