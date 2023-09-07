from time import time
from abc import ABC, abstractmethod

from system.module.logger import getlogger
from system.const import MessageType


class BaseWorker(ABC):
    def __init__(self, params=None):
        if params and isinstance(params, dict):
            for key, value in params.items():
                self.__setattr__(key, value)
            self.logger = getlogger(f"{self.worker_name}.{self.worker_id}", self.config.logger)
        self.iwork = True
        self.__msg_err_count = 0  # Кол-во сообщений с ошибками

    # Счетчик ошибочных сообщений + step
    def msg_err_count_inc(self, step=1):
        self.__msg_err_count += step

    async def start(self):
        while self.dispatcher.iwork:
            msg_send = await self.queue.get()
            self.logger.info(f"--> Обработка сообщения #{msg_send['message_num']} (ожидают в очереди => "
                             f"{self.queue.qsize()}) <--")
            time_start = time()
            try:
                res = await self.main(msg_send['route'], msg_send['message'],
                                      msg_send['message_num'], msg_type=msg_send['type'],
                                      time_incoming=msg_send['time_incoming'])
            except Exception as err:
                await self.dispatcher.stop(f"{err.__class__.__name__}: {err}" if str(err) else None)
                res = False
            if msg_send['type'] == MessageType.RABBITMQ:
                if res is True:
                    await msg_send['message'].ack()
                elif res is False:
                    await msg_send['message'].nack()
            time_end = time()
            msg_err_count_txt = f" Errors: {self.__msg_err_count} " if self.__msg_err_count else ""
            self.logger.info(f"--- Message #{msg_send['message_num']} "
                             f"time prepare: {round(time_end - time_start, 4)} "
                             f"time response: {round(time_end - msg_send['time_incoming'], 4)}{msg_err_count_txt} ---")
            self.queue.task_done()  # Элемент отработан
        self.logger.warning(f"Worker {self.worker_name} stopped!")
        self.iwork = False

    async def prepare(self):
        pass

    @abstractmethod
    async def main(self, route, message, message_num, **kwargs):
        pass
