import copy
import asyncio
import traceback
from importlib import import_module
from abc import ABC, abstractmethod

from system.const import CHAT_NAMES
from system.module.logger import getlogger


class BaseConnection(ABC):
    connection_name = None
    
    def __init__(self, params=None):
        if params and isinstance(params, dict):
            for key, value in params.items():
                self.__setattr__(key, value)
            self.logger = getlogger(self.connection_name, self.config.logger)

    @abstractmethod
    async def connection(self):
        pass

    async def close(self):
        pass


# Инициализация соединений, не относится к классу
async def init_connection(connections, params, logger, dispatcher=None, name_list_filter=None):
    if not connections or not isinstance(connections, dict):
        logger.error('No one connection!')
        return False
    for priority in set(value.get('priority', 0) for value in connections.values()):
        tasks, obj_list = [], []
        for connection_name, value in connections.items():
            if name_list_filter and connection_name not in name_list_filter:
                continue
            if value.get('priority', 0) == priority:
                connection_class_name = value['class'].split('.')[-1]
                try:
                    module = import_module(f"app.connection.{value['class']}")
                except ModuleNotFoundError as e:
                    module = import_module(f"system.connection.{connection_class_name}")
                connection_params = copy.copy(params)
                connection_params['connection_name'] = connection_name
                connection_params['values'] = value.get('values', {})
                try:
                    connection_class = getattr(module, connection_class_name)
                except AttributeError:
                    connection_class = getattr(module, 'Connection')
                if issubclass(connection_class, BaseConnection):
                    obj = connection_class(connection_params)  # Поск имени класса!!!
                    obj_list.append(obj)
                    tasks.append(obj.connection())
                    if dispatcher:
                        if connection_class_name == 'Web':
                            dispatcher.web_connection_name = connection_name  # для web
                        elif not dispatcher.chat_name and connection_class_name in CHAT_NAMES:
                            dispatcher.chat_name = connection_name  # для slack, zulip, mattermost, bitrix24
                else:
                    logger.error(f"{value['class']} не является наследником BaseConnection")
                    return False
        if tasks:
            for index, result in enumerate(await asyncio.gather(*tasks, return_exceptions=True)):
                if result is True:
                    params[obj_list[index].connection_name] = obj_list[index]
                else:
                    logger.error(result)
                    return False
        elif not name_list_filter:
            logger.error("No one connection!")
            return False
    logger.info('All connections is inited!')
    return True
