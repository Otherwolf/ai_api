# Custom Logger Using Loguru

import logging
import sys
from pathlib import Path

from loguru import logger


class InterceptHandler(logging.Handler):
    loglevel_mapping = {
        50: 'CRITICAL',
        40: 'ERROR',
        30: 'WARNING',
        20: 'INFO',
        10: 'DEBUG',
        0: 'NOTSET',
    }

    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except AttributeError:
            level = self.loglevel_mapping[record.levelno]

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        log = logger.bind(request_id='app')
        log.opt(
            depth=depth,
            exception=record.exc_info
        ).log(level, record.getMessage())


class LoguruLogger:
    instances = {}

    @classmethod
    def make_logger(cls, name_module: str, config_logger: dict):
        if name_module in cls.instances:
            return cls.instances[name_module]
        logger = cls.customize_logging(
            config_logger.get('path'),
            module=name_module,
            level=config_logger.get('level'),
            retention=config_logger.get('retention'),
            rotation=config_logger.get('rotation'),
            format=config_logger.get('format'),
            diagnose=bool(config_logger.get('diagnose', True))
        )
        handler = InterceptHandler()
        logger.handlers = [handler]
        cls.instances[name_module] = logger
        # cls.instances[f"{name_module}_id"] = id(logger.handlers)
        return logger

    @classmethod
    def customize_logging(cls,
                          filepath: Path,
                          level: str,
                          rotation: str,
                          retention: str,
                          format: str,
                          diagnose: bool,
                          module: str
                          ):
        logger.remove()
        logger.add(
            sys.stderr,
            enqueue=True,
            backtrace=True,
            level=level.upper(),
            format=format,
            diagnose=diagnose,
        )
        logger.configure(extra={"module": module})
        if filepath:
            logger.add(
                str(filepath),
                rotation=rotation,
                retention=retention,
                enqueue=True,
                backtrace=True,
                level=level.upper(),
                format=format,
                diagnose=diagnose
            )
        # logging.basicConfig(handlers=[InterceptHandler()], level=0)
        for _log in [
            # 'uvicorn.access',
            'uvicorn',
            # 'uvicorn.error',
            # 'fastapi'
        ]:
            _logger = logging.getLogger(_log)

        return logger.bind(request_id=None, method=None).bind(module=module)
