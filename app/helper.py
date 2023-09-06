import os
import urllib.request


def load_model(model_path, model_url):

    # Проверяем наличие файла с моделью
    if not os.path.isfile(model_path):

        # Загружаем модель по ссылке
        print('Start loading model...')
        urllib.request.urlretrieve(model_url, model_path)
        print("The model loaded successful")
