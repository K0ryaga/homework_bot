HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


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
