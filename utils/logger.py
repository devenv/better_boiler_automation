from datetime import datetime
import logging
from pythonjsonlogger import jsonlogger


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        if not log_record.get('timestamp'):
            # this doesn't use record.created, so it is slightly off
            now = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            log_record['timestamp'] = now
        if log_record.get('level'):
            log_record['level'] = log_record['level'].upper()
        else:
            log_record['level'] = record.levelname


def get_logger():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger()
    logger.propagate = False

    logger.handlers = []

    stdio_handler = logging.StreamHandler()
    logger.addHandler(stdio_handler)

    file_handler = logging.FileHandler('boiler.log')
    formatter = CustomJsonFormatter('%(timestamp)s %(level)s %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
