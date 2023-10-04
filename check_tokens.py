import sys
import logging


class Logger:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        file_handler = logging.FileHandler('bot.log')
        file_handler.setLevel(logging.DEBUG)

        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)


logger = Logger()


def check_tokens(tokens):
    '''
    Проверяет, присутствуют ли все необходимые токены.
    '''
    if not all(tokens):
        logger.logger.critical(
                "Программа принудительно останавливается при отсутствии "
                "обязательных переменных окружения.")
        sys.exit()
