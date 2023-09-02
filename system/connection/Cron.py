import asyncio

from datetime import datetime, timedelta

from system.connection.BaseConnection import BaseConnection


class Cron(BaseConnection):
    async def connection(self):
        return True

    # Уснуть до времени старта работы крона
    async def sleep_up_to_start_cron_hour(self, cron_name, start_cron_hour, dt=None):
        if not dt:
            dt = datetime.now()
        dt_start_cron_hour = dt.replace(hour=start_cron_hour, minute=0, second=0, microsecond=0)
        if dt_start_cron_hour < dt:
            dt_start_cron_hour += timedelta(days=1)
        sleep_seconds = (dt_start_cron_hour - dt).total_seconds()
        if sleep_seconds >= 1:
            self.logger.debug(f"Крон {cron_name} уснул на {sleep_seconds} секунд до {dt_start_cron_hour}")
            await asyncio.sleep(sleep_seconds)
