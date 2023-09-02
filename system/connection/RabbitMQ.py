import aio_pika
from aio_pika import Message
from aio_pika.pool import Pool
from collections import namedtuple
from datetime import datetime
import pytz
import orjson
from uuid import uuid4

from system.connection.BaseConnection import BaseConnection


class RabbitMQ(BaseConnection):

    @staticmethod
    def get_date_time_iso_format():
        return datetime.now(pytz.timezone('Europe/Moscow')).isoformat('T', 'seconds')

    def gen_msg(self, system_to: str, object: str, action: str, reference_id=None, msg_id=None, params=None):
        if not msg_id:
            msg_id = str(uuid4())
        if not reference_id:
            reference_id = str(uuid4())
        return {
            "system_to": str(system_to),
            "system_from": self.config.app_name,
            "object": str(object),
            "action": str(action),
            "priority": 1,
            "api_version": "1.0",
            "reference_id": str(reference_id),
            "message_id": str(msg_id),
            "datetime_created": self.get_date_time_iso_format(),
            "params": params if isinstance(params, dict) else {}
        }

    @staticmethod
    def gen_status(msg_id, errors=None):
        return {
            "request_id": str(msg_id),
            "success": not errors,
            "errors": errors if errors else [],
        }

    async def publish(self, route_key, msg):
        self.logger.info(f"Отправка сообщения в RabbitMQ {route_key=}")
        if isinstance(msg, dict):
            json_b = orjson.dumps(msg)
        elif isinstance(msg, str):
            json_b = msg.encode("utf-8")
        else:
            json_b = msg
        try:  # Отправка сообщения в RabbitMQ
            await self.exchange.publish(Message(json_b), routing_key=route_key)
        except Exception as err:
            await self.dispatcher.stop(f"{err.__class__.__name__}: {err}")

    # Отправка ответа в RabbitMQ
    async def publish_reply(self, msg, error_list, params_reply):
        msg = msg if isinstance(msg, dict) else msg.dict()
        params = params_reply if isinstance(params_reply, dict) else {}
        params['status'] = self.gen_status(msg['message_id'], error_list)
        rabbit_json = self.gen_msg(
            msg['system_from'], msg['object'], f"{msg['action']}_reply", msg['reference_id'], None, params)
        await self.publish(f"{rabbit_json['object']}.{rabbit_json['action']}", rabbit_json)

    async def bind(self, name_queue, route_key):
        if self.queue.get(name_queue):
            self.logger.warning(f"RabbitMQ: queue: {name_queue} bind {route_key=}")
            await self.queue[name_queue].bind(self.exchange, route_key)
        else:
            self.logger.error(f"RabbitMQ: Не найдена queue: {name_queue} NOT bind {route_key=}")

    async def unbind(self, name_queue, route_key):
        if self.queue.get(name_queue):
            self.logger.warning(f"RabbitMQ: queue: {name_queue} unbind {route_key=}")
            await self.queue[name_queue].unbind(self.exchange, route_key)
        else:
            self.logger.error(f"RabbitMQ: Не найдена queue: {name_queue} NOT unbind {route_key=}")

    async def get_connection(self):
        return await aio_pika.connect_robust(self.values['rabbitmq_url'], loop=self.loop)

    async def get_channel(self) -> aio_pika.Channel:
        async with self.connection_pool.acquire() as connection:
            return await connection.channel()

    # https://aio-pika.readthedocs.io/en/latest/quick-start.html#connection-pooling
    async def connection(self):
        self.connection_pool = Pool(self.get_connection,
                                    max_size=self.values['pool'].get('connection', 1), loop=self.loop)
        self.channel_pool = Pool(self.get_channel, max_size=self.values['pool'].get('channel', 1), loop=self.loop)
        # Connect to RabbitMQ
        self.queue = {}
        self.logger.warning('Подключение к RabbitMQ...')
        if 'dispatcher' in list(self.__dict__):  # Если объявлена переменная dispatcher
            dispatcher = self.dispatcher
        else:  # Иначе если библиотека подключается из вне без диспетчера
            Dispatcher = namedtuple('Dispatcher', ['channel_prefetch_count', 'queue_bindings'])
            dispatcher = Dispatcher(channel_prefetch_count=1, queue_bindings={})
        try:
            async with self.channel_pool.acquire() as channel:
                prefetch_count = self.values['queues_config'].get('prefetch_count')
                if not prefetch_count:
                    prefetch_count = dispatcher.channel_prefetch_count
                await channel.set_qos(prefetch_count=prefetch_count)
                self.exchange = await channel.declare_exchange(
                    self.values['exchange']['name'], type=self.values['exchange']['type'],
                    durable=self.values['exchange']['durable'],
                    auto_delete=self.values['exchange']['auto_delete'])
                auto_delete = self.values['queues_config'].get('auto_delete', False)
                durable = self.values['queues_config'].get('durable', True)
                arguments = self.values['queues_config'].get('arguments')
                for queue_name, queue_bindings in dispatcher.queue_bindings.items():
                    self.queue[queue_name] = await channel.declare_queue(
                        queue_name, auto_delete=auto_delete, durable=durable, arguments=arguments)
                    if self.queue[queue_name]:
                        await self.queue[queue_name].consume(dispatcher.process_message, no_ack=False)
                        for route_key in queue_bindings:  # Биндинги к очереди
                            await self.bind(queue_name, route_key)
                    else:
                        self.logger.error(f"Не удается инициализировать очередь {queue_name}!")
                        return False
                else:
                    self.logger.warning(f'RabbitMQ: успешно инициализирован!')
                    return True
        except ConnectionError:
            pass
        self.logger.error('RabbitMQ: Нет подключения к пулу каналов или очереди!')
        return False
