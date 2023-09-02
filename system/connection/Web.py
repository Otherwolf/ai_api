from aiohttp import web as aiohttp_web
# https://github.com/amitsaha/aiohttp-prometheus

from system.connection.BaseConnection import BaseConnection


class Web(BaseConnection):
    async def connection(self):
        self._myapp = aiohttp_web.Application(client_max_size=self.values.get('client_max_size', 0))
        # Работоспособность
        if health_checker := self.values.get('health_checker'):
            is_health_checker = health_checker.get('url_health') and health_checker.get('url_live')
        else:
            is_health_checker = False
        # Метрика
        if metrics := self.values.get('metrics'):
            if not isinstance(metrics, list):
                metrics = None
        if not self.dispatcher.web_urls and not is_health_checker and not metrics:
            self.logger.error("Не определены url у web-воркеров!")
            return False
        routes = []
        for url in self.dispatcher.web_urls:
            routes.append(aiohttp_web.get(url, self.dispatcher.get))
            routes.append(aiohttp_web.post(url, self.dispatcher.post))
        if is_health_checker:  # Добавляем url для проверки работоспособности
            url_health = self.dispatcher.gen_url(health_checker['url_health'])
            url_live = self.dispatcher.gen_url(health_checker['url_live'])
            self.logger.debug(f"Инициализация проверки работоспособности ({url_health=} {url_live=})")
            routes.append(aiohttp_web.get(url_health, self.dispatcher.get_healthness_reply))
            routes.append(aiohttp_web.get(url_live, self.dispatcher.get_liveness_reply))
        # Инициализация метрики
        if metrics:
            for metric_url in metrics:
                routes.append(aiohttp_web.get(self.dispatcher.gen_url(metric_url), self.dispatcher.get_metrics))
            self.logger.debug(f"Инициализация метрики: {', '.join(metrics)}")
        self._myapp.add_routes(routes)
        return True

    def run_app(self):
        self.logger.info("Web успешно инициализирован!")
        try:  # В новой версии aiohttp необходимо передавать loop
            aiohttp_web.run_app(self._myapp, host=self.values.get('host'),
                                port=self.values.get('port'), loop=self.loop)  # port=8080
        except TypeError:
            aiohttp_web.run_app(self._myapp, host=self.values.get('host'),
                                port=self.values.get('port'))  # port=8080

    async def stop(self):
        await self._myapp.cleanup()
        await self._myapp.shutdown()
