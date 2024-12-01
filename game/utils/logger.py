import logging
from aiologger.loggers.json import JsonLogger
from aiologger.handlers.files import AsyncFileHandler

# logger = JsonLogger.with_default_handlers()
# def config_async_logging(level, log_name) -> None:
#     logger.handlers.append()

def configure_logging(level, log_name) -> None:
    logging.basicConfig(filename=log_name,
                        filemode='a',
                        level=level, datefmt="%Y-%m-%d %H:%M:%S",
                        format = "[%(asctime)s.%(msecs)03d] %(module)s:%(lineno)d %(levelname)s - %(message)s")


