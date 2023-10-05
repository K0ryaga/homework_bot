import requests
import http


def get_api_answer(timestamp):
    """Делает запрос к API-сервису и возвращает ответ."""
    from homework import PRACTICUM_TOKEN, url
    headers = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
    params = {'from_date': timestamp}

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        if response.status_code != http.HTTPStatus.OK:
            raise ValueError(
                f"Ошибка при запросе к API: {response.status_code}")
        return response.json()
    except requests.RequestException as error:
        raise ValueError(f"Ошибка при запросе к API: {error}")


def check_response(response):
    """Проверяет ответ API на соответствие документации."""
    if not isinstance(response, dict):
        raise TypeError(
            f"Ожидается словарь в качестве ответа API.\n{response}")

    if "homeworks" not in response:
        raise KeyError(
            f"Отсутствует ключ 'homeworks' в ответе API.\n{response}")

    homeworks = response["homeworks"]
    if not isinstance(homeworks, list):
        raise TypeError(
            f"Ожидается список в качестве значения ключа 'homeworks'."
            f"\n{response}")

    for homework in homeworks:
        if not isinstance(homework, dict):
            raise TypeError(
                f"Ожидается словарь в списке 'homeworks'.\n{response}")

        if "homework_name" not in homework:
            raise KeyError(
                f"Отсутствует ключ 'homework_name' в словаре 'homework'."
                f"\n{response}")

        if "status" not in homework:
            raise KeyError(
                f"Отсутствует ключ 'status' в словаре 'homework'.\n{response}")
