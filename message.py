import logging
import os
import telegram


class Logger:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        file_handler = logging.FileHandler('bot.log')
        file_handler.setLevel(logging.DEBUG)

        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)


logger = Logger()


def send_message(bot, message):
    """Отправляет сообщение в Telegram чат."""
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    try:
        bot.send_message(chat_id, message)
        logger.logger.debug('Успешная отправка сообщения в Telegram')
    except telegram.error.TelegramError as error:
        logger.logger.error(f'Ошибка при отправке сообщения в Telegram: {error}')
