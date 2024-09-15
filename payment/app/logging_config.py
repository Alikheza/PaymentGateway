
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
            'publisher_file_handler': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': 'INFO',
                'formatter': 'file',
                'filename': 'logs/consumer.log', 
                'maxBytes': 1024 * 1024 * 2,
                'backupCount': 3,
                'encoding': 'utf8',
            },
            'paymentGateway_file_handler' : {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': 'INFO',
                'formatter': 'file',
                'filename': 'logs/paymentGateway.log', 
                'maxBytes': 1024 * 1024 * 5,
                'backupCount': 3,
                'encoding': 'utf8',
            }
        },
        'loggers': {

            'payment': {
                'handlers': ['info_file_handler'],
                'level': 'INFO',
                'propagate': False,
            },

            'error_logger': {
                'handlers': ['error_file_handler'],
                'level': 'ERROR',
                'propagate': False,
            },

            'publisher_logger': {
                'handlers': ['publisher_file_handler'],
                'level': 'INFO',
                'propagate': False,
            },
            'payment_gateway':{
                'handlers': ['paymentGateway_file_handler'],
                'level': 'INFO',
                'propagate': False,
            }
        },
    })