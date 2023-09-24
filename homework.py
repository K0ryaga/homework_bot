import os
import time
import telegram
import sys
import logging
from dotenv import load_dotenv


from api import check_response, get_api_answer
from status_parser import parse_status, HOMEWORK_VERDICTS
from message import send_message


load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD = 600
API_HOST = 'https://practicum.yandex.ru/api/user_api/'
ENDPOINT = 'homework_statuses/'
url = f'{API_HOST}{ENDPOINT}'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler('bot.log')
file_handler.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)


def check_tokens():
    """Проверяет, все ли переменные окружения существуют."""
    required_variables = [
        'PRACTICUM_TOKEN',
        'TELEGRAM_TOKEN',
        'TELEGRAM_CHAT_ID'
    ]
    missing_variables = []

    for variable in required_variables:
        if not os.getenv(variable):
            missing_variables.append(variable)

    if missing_variables:
        missing_variables_str = ', '.join(missing_variables)
        error_message = (
            f"Отсутствуют следующие переменные окружения: "
            f"{missing_variables_str}"
        )
        raise ValueError(error_message)

    if not os.getenv('TELEGRAM_CHAT_ID'):
        raise ValueError(
            "Переменная окружения TELEGRAM_CHAT_ID не установлена.")

    if not all([PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID]):
        logger.critical(
            "Программа принудительно останавливается при отсутствии "
            "обязательных переменных окружения.")
        sys.exit()


def main():
    """Основная логика работы программы."""
    check_tokens()
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
                    logger.debug('Успешная отправка сообщения в Telegram')
                except telegram.error.TelegramError as error:
                    logger.error(
                        f'Ошибка при отправке сообщения в Telegram: {error}')
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            send_message(bot, message)
            logger.error(message)
        time.sleep(RETRY_PERIOD)


if __name__ == "__main__":
    logger.info('Начало работы программы')
    main()
