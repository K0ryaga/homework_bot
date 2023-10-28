import time
import telegram
import logging
from dotenv import load_dotenv

from api import check_response, get_api_answer
from message import send_message
from check_tokens import check_tokens
from tokens_config import PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID
from api_config import RETRY_PERIOD, API_HOST, ENDPOINT, HEADERS
from verdicts import HOMEWORK_VERDICTS

load_dotenv()


class Logger:
    """Класс для инициализации и настройки логгера."""

    def __init__(self):
        """Инициализирует логгер и настраивает его."""
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        file_handler = logging.FileHandler('bot.log')
        file_handler.setLevel(logging.DEBUG)

        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)


logger = Logger()


def validate_homework(homework):
    """Проверяет, что homework является словарем."""
    if not isinstance(homework, dict):
        raise TypeError("Ожидается словарь в качестве параметра.")


def parse_status(homework):
    """Извлекает статус работы и возвращает строку для отправки в Telegram."""
    validate_homework(homework)

    if "homework_name" not in homework:
        raise KeyError("Отсутствует ключ 'homework_name' в словаре.")

    if "status" not in homework:
        raise KeyError("Отсутствует ключ 'status' в словаре.")

    homework_name = homework["homework_name"]
    homework_status = homework["status"]

    if homework_status not in HOMEWORK_VERDICTS:
        raise ValueError("Недопустимый статус работы.")

    verdict = HOMEWORK_VERDICTS.get(homework_status, "")
    return f'Изменился статус проверки работы "{homework_name}": {verdict}'


def main():
    """Основная логика работы программы."""
    tokens = [PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID]
    check_tokens(tokens)
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())
    url = f'{API_HOST}{ENDPOINT}'
    api_argument = url, HEADERS, timestamp
    while True:
        try:
            response = get_api_answer(api_argument)
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
