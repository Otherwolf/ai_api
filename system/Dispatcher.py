import sys
import copy
import asyncio
import aio_pika
import traceback
from aiohttp import web
from time import time
from importlib import import_module

from system.worker.BaseWorker import BaseWorker
from system.connection.BaseConnection import BaseConnection, init_connection
from system.module.counter import get_counter
from system.const import MessageType


class Dispatcher:
    def __init__(self, params):
        for index, value in params.items():
            self.__setattr__(index, value)
        self.params = params
        del self.params['logger']
        self.params['dispatcher'] = self
        self.message_num = get_counter()
        self.web_connection_name = None
        self.chat_name = None
        self.init_queue()
        self.init_metrics()
        self.iwork = True

    @staticmethod
    def gen_url(url):
        url = url.replace('\\', '/')
        if url[0] != '/':
            url = f"/{url}"
        return url

    # Инициализация очередей и роутинга к ним
    def init_queue(self):
        self.channel_prefetch_count = 0  # Максимальное число unacked-сообщений (распакованных)
        self.queue_worker = {}  # Связь наименование worker'а к какой очереди
        self.queue_bindings = {}  # Связь очередь + список binding'ов для инициализации RabbitMQ
        self.queue_route = {MessageType.RABBITMQ: {}, MessageType.WEB: {}}  # Роутинг к очереди по route_key или url
        self.web_urls = []  # Список всеx URL в конфигурации
        workers = self.config.config.get('worker')
        if workers and isinstance(workers, dict):  # Если воркеры в конфиге есть! Их может и не быть:)
            for worker_name, worker_params in workers.items():
                worker_count = worker_params.get('count', 1)
                self.queue_worker[worker_name] = {
                    'queue': asyncio.Queue(),
                    'count': worker_count,
                    'class': worker_params['class'],
                    'values': worker_params.get('values', {})
                }
                if worker_params.get('listen') == 'rabbitmq' and worker_params.get('queue') and \
                        worker_params.get('bindings'):  # Это воркер слушающий очередь RabbitMQ
                    self.channel_prefetch_count += worker_count
                    if not self.queue_bindings.get(worker_params['queue']):
                        self.queue_bindings[worker_params['queue']] = []
                    for binding in worker_params['bindings']:
                        if not self.queue_route[MessageType.RABBITMQ].get(binding):
                            self.queue_bindings[worker_params['queue']].append(binding)
                            self.queue_route[MessageType.RABBITMQ][binding] = [self.queue_worker[worker_name]['queue']]
                        else:
                            self.logger.error(f"Воркер {worker_name} не привязан к биндингу {binding}, "
                                              f"так как ранее к этому биндингу был привязан другой воркер!")
                        # self.queue_route[MessageType.RABBITMQ][binding].append(self.queue_worker[worker_name]['queue'])
                elif worker_params.get('listen') == 'web':  # Это воркер слушающий web
                    if url := worker_params.get('url'):
                        url = self.gen_url(url)
                        if not self.queue_route[MessageType.WEB].get(url):
                            self.web_urls.append(url)
                            self.queue_route[MessageType.WEB][url] = []
                        self.queue_route[MessageType.WEB][url].append(self.queue_worker[worker_name]['queue'])
                    else:
                        self.logger.error(f"Воркер {worker_name} не инициализирован, так как не указан url!")
                else:
                    self.logger.error(f"Воркер {worker_name} не инициализирован!")

    async def init_connection(self):
        return await init_connection(self.config.connection, self.params, self.logger, self)

    async def init_workers(self):
        tasks = []
        self.obj_list = []
        for worker_name, value in self.queue_worker.items():
            module = import_module(f"app.worker.{value['class']}")
            try:
                worker_class = getattr(module, value['class'].split('.')[-1])
            except AttributeError:
                worker_class = getattr(module, 'Worker')
            if issubclass(worker_class, BaseWorker):
                for worker_id in range(1, value['count'] + 1):
                    worker_params = copy.copy(self.params)
                    worker_params['queue'] = value['queue']
                    worker_params['worker_name'] = worker_name
                    worker_params['worker_id'] = worker_id
                    worker_params['values'] = value['values']
                    obj = worker_class(worker_params)
                    self.obj_list.append(obj)
                    tasks.append(obj.prepare())
            else:
                self.logger.error(f"{value['class']} не является наследником BaseWorker")
                return False
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)  # Вызов метода prepare
            for obj in self.obj_list:
                asyncio.ensure_future(obj.start())
        else:
            self.logger.warning("Запущено без воркеров!")
        return True

    #  Метрика
    def init_metrics(self):  # инициализация
        pass

    async def get_metrics(self, request):  # GET-запросы
        return web.Response(text='OK')

    #  Проверка работоспособности
    async def get_liveness_reply(self, request):
        return web.Response(status=200 if self.iwork else 503, text=str(self.iwork))

    async def get_healthness_reply(self, request):
        return web.Response(text='OK')

    # Прием post-запросов
    async def post(self, request):
        text = await request.text()
        if len(text) < self.config.message_min_length:
            self.logger.error(f"Сообщения длинной меньше {self.config.message_min_length} "
                              f"символов не обрабатываются!")
            return web.Response(status=400, text="Bad Request")
        else:
            await self.processing(MessageType.WEB, request.path, text)
            return web.Response(status=200, text="OK")

    # Прием get-запросов
    async def get(self, request):
        return web.Response(status=404, text=f"{self.config.app_name}->{self.config.app_get_info}")

    async def process_message(self, message: aio_pika.IncomingMessage):
        if message.body_size < self.config.message_min_length:
            self.logger.error(f"Сообщения длинной меньше {self.config.message_min_length} "
                              f"символов не обрабатываются!")
            await message.ack()
        else:
            await self.processing(MessageType.RABBITMQ, message.routing_key, message)

    # Общая обработка входящих сообщений
    async def processing(self, type: MessageType, route, message):
        if self.iwork is False:
            self.logger.warning("Прекращен прием новых сообщений!")
            return
        msg_err = None
        if self.queue_route.get(type):
            if els := self.queue_route[type].get(route):
                msg_send = {
                    'type': type,
                    'time_incoming': time(),
                    'route': route,
                    'message_num': next(self.message_num),
                    'message': message,
                }
                for el in els:
                    el.put_nowait(msg_send)  # await el.put(msg_send)
            else:
                msg_err = f"Для роутинга не найден биндинг = {type}.{route}"
        else:
            msg_err = f"Для роутинга не найден тип = {type}"
        if msg_err:
            self.logger.error(msg_err)
            if type == MessageType.RABBITMQ:
                await message.ack()

    # Остановка сервиса
    async def stop(self, msg_err=None):
        if msg_err:
            if self.chat_name:  # Отправка сообщения в чат
                self.params[self.chat_name].post(
                    app_name=self.config.app_name,
                    env=self.config.args.env,
                    action='Остановка сервиса',
                    exception=msg_err,
                    traceback=traceback.format_exc()
                )
            else:
                self.logger.error(f"{self.config.app_name}: {msg_err}\n{traceback.format_exc()}")
        self.iwork = False
        for _ in range(10):  # Через 10 секунд завершаем без вариантов
            await asyncio.sleep(1)
            for obj in self.obj_list:
                if obj.iwork:
                    break
            else:
                break
        # Закрытие всех соединений
        if tasks := [obj.close() for obj in self.params.values() if isinstance(obj, BaseConnection)]:
            try:
                await asyncio.gather(*tasks, return_exceptions=True)
            except Exception as err:
                self.logger.error(f"Ошибка при закрытии соединений: {err.__class__.__name__}: {err}")
        self.loop.stop()
        sys.exit()
