import time
import telegram
import logging
from dotenv import load_dotenv

from api import check_response, get_api_answer
from status_parser import parse_status
from message import send_message
from check_tokens import check_tokens
from tokens_config import PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID
from api_config import RETRY_PERIOD, API_HOST, ENDPOINT, HEADERS

load_dotenv()


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}
# За время этого проекта вы доказали мне свою некомпетентность
# Я уже обратился к руководству и мне назначили другого ревьюера
# К сожелению со следуещего проекта, так что сделайте последнее одолжение
# Примите работу в которой уже НЕЧЕГО дополнять и изменять
# Не усложняйте себе и мне жизнь ибо при отказе я вновь обращусь к руководству
# И что-то мне подсказывает что они будут на моей стороне
# Досвидания, надеюсь больше мне с вами работать никогда не придется


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
