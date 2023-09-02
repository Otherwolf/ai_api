import asyncio

from app.Dispatcher import Dispatcher


class Daemon:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger

    async def init_app(self, dispatcher):
        if await dispatcher.init_connection():
            return await dispatcher.init_workers()
        return False

    def run(self):
        self.logger.info("Старт сервиса!")
        loop = asyncio.get_event_loop()
        dispatcher = Dispatcher({
            'config': self.config,
            'logger': self.logger,
            'loop': loop,
        })
        if loop.run_until_complete(self.init_app(dispatcher)):
            if dispatcher.web_connection_name:  # Это web
                dispatcher.params[dispatcher.web_connection_name].run_app()
            else:
                try:
                    loop.run_forever()
                except KeyboardInterrupt:
                    pass
        self.logger.error('Сервис остановлен!')
