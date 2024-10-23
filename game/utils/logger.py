import logging

def configure_logging(level, log_name) -> None:
    logging.basicConfig(filename=log_name,
                        filemode='a',
                        level=level, datefmt="%Y-%m-%d %H:%M:%S",
                        format = "[%(asctime)s.%(msecs)03d] %(module)s:%(lineno)d %(levelname)s - %(message)s")


