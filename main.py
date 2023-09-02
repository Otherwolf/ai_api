from system_ync.Daemon import Daemon
from system_ync.module.logger import get_logger
from system_ync.module.ymlconfig import YmlConfig, get_arguments


if __name__ == "__main__":
    config = YmlConfig(*get_arguments())
    logger = get_logger(f'{config.app_name}_main', config.logger)
    Daemon(config, logger).run()
