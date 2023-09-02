from sentry_sdk import init, set_level, utils

from system.connection.BaseConnection import BaseConnection


class Sentry(BaseConnection):
    async def connection(self):
        init(
            self.values['dsn'],
            traces_sample_rate=0,
            max_breadcrumbs=100,
            debug=False,
            attach_stacktrace=True,
            with_locals=True,
            environment=self.config.args.env
        )
        set_level(self.config.logger['level'].lower())
        utils.MAX_STRING_LENGTH = 1000
        self.logger.info('Подключение к Sentry')
        return True
