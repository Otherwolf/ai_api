# https://cloud.yandex.ru/docs/storage/tools/boto
import boto3
from botocore.exceptions import ClientError
from time import sleep

from system.connection.BaseConnection import BaseConnection


class S3(BaseConnection):
    async def connection(self):
        return self.connect()

    def connect(self):
        try:
            session = boto3.session.Session()
            self.s3 = session.client(
                service_name='s3',
                aws_access_key_id=self.values['access_key_id'],
                aws_secret_access_key=self.values['secret_access_key'],
                endpoint_url=self.values['endpoint_url']
            )
            self.logger.info("S3 подключен!")
            return True
        except Exception as err:
            self.logger.error(f"S3 не подключен! Ошибка: {err}")
            return False

    # Список объектов в корзине
    def list_objects(self, bucket_name=None):
        if bucket_name is None:
            bucket_name = self.values['bucket_name']
        list_obj = []
        for obj in self.s3.list_objects(Bucket=bucket_name).get('Contents', []):
            list_obj.append(obj)
        return list_obj

    # Добавление объекта в корзину
    def put_object(self, bucket_name, key, data):
        if bucket_name is None:
            bucket_name = self.values['bucket_name']
        for time_sleep in (3, 5, 0):
            try:
                self.s3.put_object(Bucket=bucket_name, Key=key, Body=data)
                return True
            except self.s3.exceptions.ClientError as err:
                self.logger.error(f"{err.__class__.__name__}: {err}")
                sleep(time_sleep)
                self.connect()  # Пепеподключение к S3
        return False

    # Получение объекта из корзины
    def get_object(self, bucket_name, key):
        if bucket_name is None:
            bucket_name = self.values['bucket_name']
        try:
            get_object_response = self.s3.get_object(Bucket=bucket_name, Key=key)
            return get_object_response['Body'].read()
        except self.s3.exceptions.NoSuchKey as err:
            self.logger.error(f'Ошибка при получении объекта из S3: {err}')

    #  Удаление объектов из S3
    def delete_objects(self, bucket_name, key_list):
        if key_list:
            if bucket_name is None:
                bucket_name = self.values['bucket_name']
            for_deletion = [{'Key': key} for key in key_list]
            return self.s3.delete_objects(Bucket=bucket_name, Delete={'Objects': for_deletion})

    # Получить временную ссылку на объект
    # https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-presigned-urls.html
    def generate_presigned_url(self, bucket_name, key, expiration=3600):
        if bucket_name is None:
            bucket_name = self.values['bucket_name']
        try:
            return self.s3.generate_presigned_url(
                'get_object', Params={'Bucket': bucket_name, 'Key': key}, ExpiresIn=expiration)
        except ClientError as err:
            self.logger.error(f"{err.__class__.__name__}: {err}")
