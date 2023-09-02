import asyncio
from aiobotocore.session import get_session
from botocore.exceptions import ClientError

from system.connection.BaseConnection import BaseConnection


def client_context(fnc):
    async def wrapper(*args, **kwargs):
        self = args[0]
        async with self.session.create_client(
            service_name='s3',
            aws_access_key_id=self.values['access_key_id'],
            aws_secret_access_key=self.values['secret_access_key'],
            endpoint_url=self.values['endpoint_url']
        ) as client:
            return await fnc(self, client, *args[1:], **kwargs)
    return wrapper


class S3AioBotoCore(BaseConnection):
    async def connection(self):
        self.session = get_session()
        self.show_message = False
        try:
            await self.get_object(self.values['bucket_name'], 'test')
            self.logger.info("S3 подключен!")
            self.show_message = True
            return True
        except ClientError as err:
            self.logger.error(f"S3 не подключен! Ошибка: {err}")
            return False

    @client_context  # Список объектов в корзине
    async def list_objects(self, client, bucket_name=None, is_entire_obj=False):
        if bucket_name is None:
            bucket_name = self.values['bucket_name']
        list_obj = []
        paginator = client.get_paginator('list_objects')
        async for result in paginator.paginate(Bucket=bucket_name):
            for obj in result.get('Contents', []):
                list_obj.append(obj if is_entire_obj else obj['Key'])
        return list_obj

    @client_context  # Получение объекта из корзины
    async def get_object(self, client, bucket_name, key):
        if bucket_name is None:
            bucket_name = self.values['bucket_name']
        try:
            get_object_response = await client.get_object(Bucket=bucket_name, Key=key)
            return await get_object_response['Body'].read()
        except client.exceptions.NoSuchKey as err:
            if self.show_message:
                self.logger.error(f'Ошибка при получении объекта {key} из S3: {err}')

    @client_context  # Добавление объекта в корзину
    async def put_object(self, client, bucket_name, key, data):
        if bucket_name is None:
            bucket_name = self.values['bucket_name']
        for time_sleep in (3, 5, 10):
            try:
                await client.put_object(Bucket=bucket_name, Key=key, Body=data)
                return True
            except ClientError as err:
                if self.show_message:
                    self.logger.error(f"{err.__class__.__name__}: {err}")
                await asyncio.sleep(time_sleep)
        return False

    @client_context  # Удаление объектов из S3
    async def delete_objects(self, client, bucket_name, key_list):
        if bucket_name is None:
            bucket_name = self.values['bucket_name']
        if key_list:
            for_deletion = [{'Key': key} for key in key_list]
            return await client.delete_objects(Bucket=bucket_name, Delete={'Objects': for_deletion})

    @client_context  # Получить временную ссылку на объект
    async def generate_presigned_url(self, client, bucket_name, key, expiration=3600):
        if bucket_name is None:
            bucket_name = self.values['bucket_name']
        try:
            return await client.generate_presigned_url(
                'get_object', Params={'Bucket': bucket_name, 'Key': key}, ExpiresIn=expiration)
        except ClientError as err:
            self.logger.error(f"{err.__class__.__name__}: {err}")

    @client_context # Запросить метадату по ключу (удобно для проверки наличия ключа в s3)
    async def get_object_metadata(self, client, bucket_name, key):
        if bucket_name is None:
            bucket_name = self.values['bucket_name']
        try:
            get_object_response = await client.head_object(Bucket=bucket_name, Key=key)
            return get_object_response
        except ClientError as err:
            if self.show_message:
                self.logger.debug(f'Ошибка при получении объекта {key} из S3: {err}')
