import logging
import requests
from typing import Union, Any, NoReturn


logger = logging.getLogger(__name__)


class WordstatAPIError(Exception):
    """
    Базовое исключение для API вордстата.
    """
	pass


class Wordstat(object):
    """
    API интерфейс для работы с Яндекс.Вордстат
    """
    API_URL = 'https://api.direct.yandex.ru/v4/json/'

    def __init__(self, token: str) -> None:
        """
        Инициализация.
        :param token: Токен для доступа к API.
        """
        self.token = token

    def _prepare_params(self, params: dict[str, Union[dict, list, str]]) -> dict[str, Union[dict, list, str]]:
        """
        Подготавливает параметры для запроса.
        :param params: Параметры запроса.
        """
        return params.update({
            "locale": "ru",
            "token": self.token
        })

    def _process_response(self, response: dict[str, str]) -> Union[int, list]:
        """
        Обработать ответ от Яндекс.Вордстат.
        :param response: Данные полученные от API Яндекс.Вордстат.
        """
        if response.get('error_code'):
            raise WordstatAPIError(f'Ошибка API Яндекс.Вордстат: {response}')
        try:
            result = response['data']
        except AttributeError:
            raise WordstatAPIError(f'Неизвестный формат ответа от API Яндекс.Вордстат: {response}')
        return result   

    def create_report(self, phrases: list[str], geo_id: list[int]=[]) -> Union[int, list]:
        """
        Запускает на сервере формирование отчета о статистике поисковых запросов.
        Метод возвращает идентификатор будущего отчета.
        Формирование отчета обычно занимает до одной минуты.
        :param phrases: Список ключевых фраз, по которым требуется получить статистику поисковых запросов (не более 10 фраз в кодировке UTF-8).
        Ключевые фразы могут содержать минус-фразы. Минус-фразу из нескольких слов следует заключить в скобки, 
        например: холодильник -морозильник -(морозильная камера) -ремонт.
        Один пользователь за сутки может получить статистику поисковых запросов для 1000 фраз.
        Для одного запроса допускается отправка до 10 фраз.

        :param geo_id: Список идентификаторов регионов.
        Чтобы исключить регион, перед его идентификатором ставят минус, например [1,-219]. Значение 0 игнорируется.
        Если регионы не указаны статистика выдается по всем регионам.
        """
        if len(phrases) > 10:
            logger.warning('Для одного запроса допускается отправка до 10 фраз. Статистика по остальным фразам не будет получена.')
        params = {
            "method": "CreateNewWordstatReport",
            "param": {
                "Phrases": phrases,
                "GeoID": geo_id,
            },
        }
        response = requests.post(self.API_URL, json=self._prepare_params(params))
        response.raise_for_status()
        return self._process_response(response.json())

    def delete_report(self, report_id: int) -> Union[int, list]:
        """
        Удаляет отчет о статистике поисковых запросов.
        Отчеты удаляются автоматически через 5 часов после формирования. 
        Удалять отчеты вручную следует в случае, когда сформировано максимальное количество отчетов (пять) 
        и нужно сформировать новый отчет.
        :param report_id: ID отчета.
        """
        params = {
            "method": "DeleteWordstatReport",
            "param": report_id,
        }
        response = requests.post(self.API_URL, json=self._prepare_params(params))
        response.raise_for_status()
        return self._process_response(response.json())

