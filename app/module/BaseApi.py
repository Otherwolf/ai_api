
class BaseApi:
    def __init__(self, params, logger, config):
        for key, value in params.items():
            self.__setattr__(key, value)
        self.logger = logger
        self.config = config
