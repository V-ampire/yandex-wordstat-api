import logging
import requests
from typing import Union, Any, Optional, Dict, List

from .entities import WordstatReportInfo, WordstatReportStatusInfo


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

    def _process_request(self, params: Dict[str, Union[Dict, List, str]], headers: Dict[str, str]={}) -> Dict[str, Any]:
        """
        Выполнить запрос к API Яндекс.Вордстат.
        :param params: Входные данные.
        :param headers: Заголовки запроса.
        """
        params.update({
            "locale": "ru",
            "token": self.token
        })
        headers['User-Agent'] = "Yandex.Wordstat.API/Python"
        response = requests.post(self.API_URL, json=params, headers=headers)
        response.raise_for_status()
        return response.json()

    def _process_response(self, response: Dict[str, Any]) -> Union[int, List]:
        """
        Обработать ответ от Яндекс.Вордстат.
        :param response: Данные полученные от API Яндекс.Вордстат.
        """
        if response.get('error_code'):
            raise WordstatAPIError(f'Ошибка API Яндекс.Вордстат: {response}')
        try:
            result = response['data']
        except KeyError:
            raise WordstatAPIError(f'Неизвестный формат ответа от API Яндекс.Вордстат: {response}')
        return result   

    def create_report(self, phrases: List[str], geo_ids: List[int]=[]) -> int:
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
                "GeoID": geo_ids,
            },
        }
        return self._process_response(self._process_request(params))

    def delete_report(self, report_id: int)  -> int:
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
        return self._process_response(self._process_request(params))

    def get_report(self, report_id: int) -> WordstatReportInfo:
        """
        Возвращает отчет о статистике поисковых запросов.
        :param report_id: ID отчета.
        """
        params = {
            "method": "GetWordstatReport",
            "param": report_id,
        }
        report_data = self._process_response(self._process_request(params))
        return WordstatReportInfo(**report_data)

    def get_report_list(self) -> List[WordstatReportStatusInfo]:
        """
        Возвращает список сформированных и формируемых отчетов о статистике поисковых запросов.
        """
        params = {
            "method": "GetWordstatReportList"
        }
        report_list = self._process_response(self._process_request(params))
        return [WordstatReportStatusInfo(**report_data) for report_data in report_list]

