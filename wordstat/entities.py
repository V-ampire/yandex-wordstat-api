from typing import NamedTuple


class WordstatItem (NamedTuple):
    """
    Статистика поисковых запросов, соответствующих фразе.
    :attr phrase: Фраза, для которой приведена статистика (указана при формировании отчета).
    :attr shows: Количество поисковых запросов за прошедший месяц.
    """
    phrase: str
    shows: int


class WordstatReportInfo(NamedTuple):
    """
    Содержит статистику поисковых запросов по одной фразе.
    :attr phrase: Фраза, для которой приведена статистика (указана при формировании отчета).
    :attr geo_id: Список с идентификаторами регионов (указаны при формировании отчета).
    :attr searched_width: Статистика поисковых запросов, соответствующих фразе.
    :attr searched_also: Статистика других поисковых запросов, которые также делали потребители, искавшие фразы из списка SearchedWith
    """
    phrase: str
    geo_id: list[int]
    searched_width: list[WordstatItem]
    searched_also: list[WordstatItem]


class WordstatReportStatusInfo(NamedTuple):
    """
    Содержит сведения об одном отчете.
    :attr report_id: Идентификатор отчета о статистике поисковых запросов.
    :attr status_report: Состояние отчета:
        Done — отчет сформирован;
        Pending — отчет формируется;
        Failed — сформировать отчет не удалось.
    """
    report_id: int
    status_report: str # FIXME Сделать Enum?
