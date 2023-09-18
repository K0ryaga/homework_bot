import os
import requests
import time
import telegram
import logging
import sys
from dotenv import load_dotenv

load_dotenv()

PRACTICUM_TOKEN = 'y0_AgAAAABVwHD5AAYckQAAAADsoTDLIizCyOBVR1Clmgnoobd-L6Ny0To'
TELEGRAM_TOKEN = '5994529498:AAEFf8IuLiAIRqdUnNX_sLE0UKYdsIUZ8Oo'
TELEGRAM_CHAT_ID = '667715050'

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


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
            f"{missing_variables_str}")
        raise ValueError(error_message)


def send_message(bot, message):
    """Отправляет сообщение в Telegram чат."""
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not chat_id:
        raise ValueError(
            "Переменная окружения TELEGRAM_CHAT_ID не установлена.")

    try:
        bot.send_message(chat_id, message)
        logging.debug('Успешная отправка сообщения в Telegram')
    except telegram.error.TelegramError as error:
        logging.error(f'Ошибка при отправке сообщения в Telegram: {error}')


def get_api_answer(timestamp):
    """Делает запрос к API-сервису и возвращает ответ."""
    url = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
    headers = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
    params = {'from_date': timestamp}

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        if response.status_code != 200:
            raise ValueError(
                f"Ошибка при запросе к API: {response.status_code}")
        return response.json()
    except requests.RequestException as error:
        raise ValueError(f"Ошибка при запросе к API: {error}")


def check_response(response):
    """Проверяет ответ API на соответствие документации."""
    if not isinstance(response, dict):
        raise TypeError("Ожидается словарь в качестве ответа API.")

    if "homeworks" not in response:
        raise KeyError("Отсутствует ключ 'homeworks' в ответе API.")

    homeworks = response["homeworks"]
    if not isinstance(homeworks, list):
        raise TypeError(
            "Ожидается список в качестве значения ключа 'homeworks'.")

    for homework in homeworks:
        if not isinstance(homework, dict):
            raise TypeError("Ожидается словарь в списке 'homeworks'.")

        if "homework_name" not in homework:
            raise KeyError(
                "Отсутствует ключ 'homework_name' в словаре 'homework'.")

        if "status" not in homework:
            raise KeyError("Отсутствует ключ 'status' в словаре 'homework'.")


def parse_status(homework):
    """Извлекает статус работы и возвращает строку для отправки в Telegram."""
    if not isinstance(homework, dict):
        raise TypeError("Ожидается словарь в качестве параметра.")

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


logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='bot.log'
)


def main():
    """Основная логика работы программы."""
    check_tokens()
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())

    if not all([PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID]):
        logging.critical((
            "Программа принудительно останавливается при отсутствии"
            "обязательных переменных окружения."))
        sys.exit()
    while True:
        try:
            response = get_api_answer(timestamp)
            check_response(response)
            for homework in response["homeworks"]:
                message = parse_status(homework)
                try:
                    send_message(bot, message)
                    logging.debug('Успешная отправка сообщения в Telegram')
                except telegram.error.TelegramError as error:
                    logging.error(
                        f'Ошибка при отправке сообщения в Telegram: {error}')
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            send_message(bot, message)
            logging.error(message)
        time.sleep(RETRY_PERIOD)


if __name__ == "__main__":
    logging.info('Начало работы программы')
    main()
