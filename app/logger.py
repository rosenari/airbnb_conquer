import os
import logging
from app.constants import LOG_DIR


logger_list = [
    {
        'name': 'sqlalchemy.engine',
        'level': logging.INFO
    },
    {
        'name': 'app',
        'level': logging.INFO,
        'formatter': logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    }
]


def init_logger():
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

    logging.basicConfig(level=logging.NOTSET)
    for log_info in logger_list:
        logger = logging.getLogger(log_info['name'])
        logger.addHandler(
            get_file_handler(
                file_path=os.path.join(LOG_DIR, f"{log_info['name']}.log"),
                level=log_info['level'],
                formatter=log_info.get('formatter')
            )
        )

        logger.setLevel(log_info['level'])


def get_logger(name='dev'):
    return logging.getLogger(name)


def get_file_handler(file_path, level, formatter=None):
    handler = logging.FileHandler(file_path)
    handler.setLevel(level)
    if formatter:
        handler.setFormatter(formatter)
    return handler
