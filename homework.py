import os
import time
import telegram

import logging
from dotenv import load_dotenv

from api import check_response, get_api_answer
from status_parser import parse_status
from message import send_message
from check_tokens import check_tokens

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD = 600
API_HOST = 'https://practicum.yandex.ru/api/user_api/'
ENDPOINT = 'homework_statuses/'
url = f'{API_HOST}{ENDPOINT}'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


class Logger:
    """
    Класс для инициализации и настройки логгера.
    """

    def __init__(self):

        """Инициализирует логгер и настраивает его"""

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        file_handler = logging.FileHandler('bot.log')
        file_handler.setLevel(logging.DEBUG)

        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)
    # Настройку логгера нельзя убрать из homework.py
    # pytest написан так чтобы проверять ее исключительно здесь
    # мне подтвердили это наставники в пачке(ссылка ниже)
    # https://app.pachca.com/chats?thread_id=2049929


logger = Logger()


def main():
    """Основная логика работы программы."""
    tokens = [PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID]
    check_tokens(tokens)
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())
    while True:
        try:
            response = get_api_answer(timestamp)
            check_response(response)
            for homework in response["homeworks"]:
                message = parse_status(homework)
                try:
                    send_message(bot, message)
                    logger.logger.debug(
                        'Успешная отправка сообщения в Telegram')
                except telegram.error.TelegramError as error:
                    logger.logger.error(
                        f'Ошибка при отправке сообщения в Telegram: {error}')
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            send_message(bot, message)
            logger.logger.error(message)
        time.sleep(RETRY_PERIOD)


if __name__ == "__main__":
    logger.logger.info('Начало работы программы')
    main()
