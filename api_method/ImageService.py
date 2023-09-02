from typing import Tuple, Optional, List, Dict

import aiohttp

from app.module.BaseApi import BaseApi


class ImageService(BaseApi):

# ---------------------- NSFW detect ------------------------------------
    nsfw_categories = ('porn', 'hentai', 'sexy',)
    safe_categories = ('drawings', 'neutral',)

    nsfw_params = {
        'porn': 50,
        'hentai': 50,
        'sexy': 80
    }

    async def nsfw_detect_handler(self, image_url: str, safe_coefficient: float) \
            -> Tuple[Optional[dict], Optional[list]]:
        try:
            predicted_result = await self.nsfw_detect.classify(image_url)
            result = {'categories': predicted_result, 'is_safe': self.is_safe(predicted_result, safe_coefficient)}
            return result, None
        except (TypeError,
                aiohttp.client_exceptions.ClientResponseError,
                aiohttp.client_exceptions.ClientConnectorError) as e:
            return None, self._form_image_url_error()

    def is_safe(self, prediction: Dict[str, float], safe_coefficient: float) -> bool:
        """
        На основе предсказания нейронки формируем окончательное мнение для nsfw
        :param prediction:
        :param safe_coefficient:
        :return:
        """
        neutral_limit = 0
        if not prediction:
            return False

        for classification in prediction.keys():
            limit = self.nsfw_params.get(classification)
            if limit and prediction[classification] > (limit * safe_coefficient):
                return False
            if not limit:
                neutral_limit += prediction[classification]
        return neutral_limit > 50

# ---------------------- AESTHETIC scorer ------------------------------

    async def quality_scorer_handler(self, image_url: str)\
            -> Tuple[Optional[dict], Optional[list]]:
        try:
            predicted_result = await self.aesthetics.classify(image_url)
            return predicted_result, None
        except (TypeError,
                aiohttp.client_exceptions.ClientResponseError,
                aiohttp.client_exceptions.ClientConnectorError) as e:
            return None, self._form_image_url_error()

# ---------------------------- classificator --------------------------

    async def classify_image(self, image_url: str, labels: List[str]):
        try:
            predicted_result = await self.classificator.classify(image_url, labels)
            return predicted_result, None
        except (TypeError,
                aiohttp.client_exceptions.ClientResponseError,
                aiohttp.client_exceptions.ClientConnectorError) as e:
            return None, self._form_image_url_error()

# ----------------------- other ---------------------------------
    @staticmethod
    def _form_image_url_error():
        return [{
                "error_code": "url_parsing",
                "error_field": "QUERY.IMAGE_URL",
                "error_text": "Input should be a valid URL, relative URL without a base"
            }]