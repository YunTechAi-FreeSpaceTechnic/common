from logging.config import dictConfig
import logging


def setup_logger(debug: bool = False):
    dictConfig({
        'version': 1,
        'formatters': {
            'default': {
                'format':
                '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'stream': 'ext://sys.stdout',
                'formatter': 'default'
            }
        },
        'root': {
            'level': 'INFO',
            'handlers': ['console']
        },
    })
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG if debug else logging.INFO)
