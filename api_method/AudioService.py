import io
import time

from app.module.BaseApi import BaseApi


class AudioService(BaseApi):
    async def stt(self, audio, language: str):
        audio_bytes = io.BytesIO(await audio.read())
        if language == 'auto':
            language = None

        t = time.time()
        segments, _ = await self.whisper.recognize(audio_bytes, language)
        text = ' '.join([segment.text for segment in list(segments)])
        print('step: ', time.time() - t)
        return text.strip(), None
