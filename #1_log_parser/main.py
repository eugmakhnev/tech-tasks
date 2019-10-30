"""
Условие задания:

Пользователи посещают сайт магазина Shop. Они могут приходить из поисковиков (органический трафик),
приходить по партнерским ссылкам нескольких кэшбек-сервисов: нашего (Ours) и других (Theirs1, Theirs2).

Примеры логов в БД сервиса Ours, которые собираются скриптом со всех страниц сайта магазина:
1) Органический переход клиента в магазин
{
	"client_id": "user15",
"User-Agent": "Firefox 59",
	"document.location": "https://shop.com/products/?id=2",
	"document.referer": "https://yandex.ru/search/?q=купить+котика",
	"date": "2018-04-03T07:59:13.286000Z"
}

2) Переход клиента в магазин по партнерской ссылке кэшбек-сервиса
{
	"client_id": "user15",
	"User-Agent": "Firefox 59",
	"document.location": "https://shop.com/products/id?=2",
	"document.referer": "https://referal.ours.com/?ref=123hexcode",
	"date": "2018-04-04T08:30:14.104000Z"
}

{
	"client_id": "user15",
	"User-Agent": "Firefox 59",
	"document.location": "https://shop.com/products/id?=2",
	"document.referer": "https://ad.theirs1.com/?src=q1w2e3r4",
	"date": "2018-04-04T08:45:14.384000Z"
}

3) Внутренний переход клиента в магазине
{
	"client_id": "user15",
	"User-Agent": "Firefox 59",
	"document.location": "https://shop.com/checkout",
	"document.referer": "https://shop.com/products/id?=2",
	"date": "2018-04-04T08:59:16.222000Z"
}

Магазин Shop платит кэшбек-сервисам за клиентов, которые перешли по их ссылке, оплатили товар и в конце
попали на страницу https://shop.com/checkout (“Спасибо за заказ”). Комиссия выплачивается
по принципу “выигрывает последний кэшбек-сервис, после перехода по партнерской ссылке которого клиент купил товар”.

Сервис Ours хочет по своим логам находить клиентов, которые совершили покупку именно благодаря ему.
Нужно написать программу, которая ищет победившие партнерские ссылки сервиса Ours.
Учесть различные сценарии поведения клиента на сайте.

"""

import typing as T
from datetime import datetime

from lib import Solution, LogRecord


def deserialize_json(logs: T.List[T.Dict]) -> T.List[LogRecord]:
    return [
        LogRecord(
            id=log["client_id"] + '-' + log["User-Agent"],  # is this pair true client / device identifier ?
            created_at=datetime.strptime(log["date"], "%Y-%m-%dT%H:%M:%S.%fZ"),
            location=log["document.location"],
            referer=log.get("document.referer"),
        ) for log in logs
    ]


if __name__ == '__main__':
    import json

    with open("logs.json", "r") as f:
        records = deserialize_json(json.load(f))

    for our_sale in Solution.with_attribution_approach(records):
        print(our_sale)
