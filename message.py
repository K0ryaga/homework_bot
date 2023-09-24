import logging
import os
import telegram

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler('bot.log')
file_handler.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)


def send_message(bot, message):
    """Отправляет сообщение в Telegram чат."""
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    try:
        bot.send_message(chat_id, message)
        logging.debug('Успешная отправка сообщения в Telegram')
    except telegram.error.TelegramError as error:
        logging.error(f'Ошибка при отправке сообщения в Telegram: {error}')
