from system.module.loggers.LoguruLogger import LoguruLogger

import colorlog


def getlogger(name_module, config_logger=None):
    if config_logger is None:
        config_logger = {}
    if config_logger.get('type') == 'loguru':
        logger = LoguruLogger.make_logger(name_module, config_logger)
    else:
        handler = colorlog.StreamHandler()
        handler.setFormatter(colorlog.ColoredFormatter(
            config_logger.get('format', '%(log_color)s %(asctime)s %(name)s: %(message)s')
        ))
        logger = colorlog.getLogger(name_module)
        logger.addHandler(handler)
        logger.setLevel(config_logger.get('level', 'DEBUG'))
    return logger
