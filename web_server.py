from typing import List, Optional

from fastapi import File, UploadFile, Query
from pydantic import Field, AnyUrl

import api_method as api
from app import const
from app.const import API_V1
from system.module.WebAPI import WebAPI


method = {}
implementation = {
    api.ImageService: (const.NSFW_NAME, const.AESTHETICS_NAME, const.CLASSIFICATOR_NAME)
}

app = WebAPI(
    title='ai api',
    cors=True,
    openapi_url=f'{API_V1}/openapi.json',
    docs_url=f'{API_V1}/openapi'
)


def get_request(success, errors, result=None):
    request = {'status': {'success': success, 'errors': errors}}
    if result:
        request['result'] = result
    return request


@app.get("/", include_in_schema=False)
async def index():
    return {"ping": 'OK'}


@app.post(f"{API_V1}/image/classify", tags=['Image service'], openapi_extra={'model': const.CLASSIFICATOR_NAME})
async def image_classify_view(
        labels: List[str] = Query(None),
        image: UploadFile = File(None, description='Image content'),
        image_url: Optional[AnyUrl] = Query(None, description='HTTP/HTTPS Link to image')
):
    """
    Нейронка классифицирует картинку по списку из lables
    """
    if image_url:
        image_url = str(image_url)

    if not image_url and not image:
        return get_request(False, 'Image or image_url are required', None)

    result, e = await method[const.CLASSIFICATOR_NAME].classify_image(image_url or image, labels)
    return get_request(bool(result), e, result)


@app.post(f"{API_V1}/image/nsfw_detect", tags=['Image service'], openapi_extra={'model': const.NSFW_NAME})
async def image_nsfw_detect_view(
        safe_coefficient: Optional[float] = Query(default=1, le=2, ge=0.2,
                                                  description='Коэффициент преобразования для регулирования чувствительности на nsfw контент. Выше коэффициент = меньше чувствительность'),
        image: UploadFile = File(None, description='Image content'),
        image_url: Optional[AnyUrl] = Query(None, description='HTTP/HTTPS Link to image')
):
    """
    Определяет содержание nsfw на картинке. Принимает либо ссылку на картинку, либо содержимое картинки
    :return:
    """
    if image_url:
        image_url = str(image_url)

    if not image_url and not image:
        return get_request(False, 'Image or image_url are required', None)

    result, e = await method[const.NSFW_NAME].nsfw_detect_handler(image_url or image, safe_coefficient)
    return get_request(bool(result), e, result)


@app.post(f"{API_V1}/image/quality_scorer", tags=['Image service'], openapi_extra={'model': const.AESTHETICS_NAME})
async def image_quality_scorer_view(
        image: UploadFile = File(None, description='Image content'),
        image_url: Optional[AnyUrl] = Query(None, description='HTTP/HTTPS Link to image')
):
    """
    Определяет качество картинки. Принимает либо ссылку на картинку, либо содержимое картинки.
    Rating ~1-10 (high is good); Artifacts ~1-5 (low is good)
    """
    if image_url:
        image_url = str(image_url)

    if not image_url and not image:
        return get_request(False, 'Image or image_url are required', None)

    result, e = await method[const.AESTHETICS_NAME].quality_scorer_handler(image_url or image)
    return get_request(bool(result), e, result)


@app.on_event("startup")
async def startup():
    await app.init_connection()

    if app.connection:
        for class_object, list_of_services in implementation.items():
            api_service = class_object(app.connection, app.logger, app.config)
            for service in list_of_services:
                if service in app.connection:
                    method[service] = api_service

    # Убираю из openapi эндпоинты которые не подключены в конфиге
    for route in app.routes:
        extra_data = route.__dict__.get('openapi_extra')
        if extra_data and (model := extra_data.get('model')):
            if model not in method:
                route.__dict__['include_in_schema'] = False


if __name__ == '__main__':
    app.run('web_server:app', host=app.config.web_server.get('host', '0.0.0.0'), port=app.config.web_server['port'],
            reload=True, log_level=app.config.web_server.get('log_level', 'error'))
