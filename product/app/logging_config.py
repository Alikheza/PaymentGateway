
from logging.config import dictConfig


def configure_logging() -> None:
    dictConfig({
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'file': {
                'format': "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
                'datefmt': "%Y-%m-%d %H:%M:%S"
            },
        },
        'handlers': {
            'info_file_handler': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': 'INFO',
                'formatter': 'file',
                'filename': 'logs/general.log',  
                'maxBytes': 1024 * 1024,
                'backupCount': 3,
                'encoding': 'utf8',
            },
            'error_file_handler': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': 'ERROR',
                'formatter': 'file',
                'filename': 'logs/errors.log',
                'maxBytes': 1024 * 1024 * 5,
                'backupCount': 3,
                'encoding': 'utf8',
            },
            'consumer_file_handler': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': 'INFO',
                'formatter': 'file',
                'filename': 'logs/consumer.log', 
                'maxBytes': 1024 * 1024 * 2,
                'backupCount': 3,
                'encoding': 'utf8',
            }
        },
        'loggers': {

            'product': {
                'handlers': ['info_file_handler'],
                'level': 'INFO',
                'propagate': False,
            },

            'error_logger': {
                'handlers': ['error_file_handler'],
                'level': 'ERROR',
                'propagate': False,
            },

            'consumer_logger': {
                'handlers': ['consumer_file_handler'],
                'level': 'INFO',
                'propagate': False,
            },
        },
    })