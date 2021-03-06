import re
import typing as T
from dataclasses import dataclass
from datetime import datetime

# --- CONSTANTS ---
SALE_LOCATION = "https://shop.com/checkout"
ATTRIBUTION_WINDOW = 24  # hours


# --- TYPES ---
@dataclass
class LogRecord:
    id: str
    created_at: datetime
    location: str
    referer: T.Optional[str]  # in practice we can have no referrer (direct requests, from bookmarks and so on)


# --- UTILS ---
def handle_ref_link(referer: str) -> (bool, bool):
    """
    Check that ref belong to us or our competitor

    :param referer: http referer string
    :return: is_affiliate_link, is_our_link - tuple of flags
    """
    basic_pattern = r'^http(s)?://([a-z0-9\-]*\.)*({})/.*'

    # --- Handle our domain ---
    our_domain = "referal.ours.com"
    if re.compile(basic_pattern.format(re.escape(our_domain))).search(referer):
        return True, True

    # --- Handle competitor domains ---
    competitor_domains = {"theirs1.com"}
    if re.compile(basic_pattern.format("|".join(
            [re.escape(domain) for domain in competitor_domains]
    ))).search(referer):
        return True, False

    return False, False


# --- SOLUTIONS ---
class Solution:
    @staticmethod
    def with_attribution_approach(log_records: T.List[LogRecord]) -> T.List[LogRecord]:
        """
        Возможно, я неправильно понял условия задачи, но буду исходить из своих знаний того, как работает трекинг
        действий. У нас есть окно аттрибуции - максимальное время, за которое некое совершенное действие связывается с
        другим, его породившим. В нашем случае связь продажи с кликом по партнерской ссылке. В таком подходе нам
        абсолютно неважен путь пользователя от входа на сайт до продажи. Он вообще, может сначала зайти на сайт, сохранить
        в закладки, через час зайти из закладок (referer = null) и сделать покупку совершенно другого товара,
        чем тот, на который перешел по партнерской ссылке. Таким образом задача сводится лишь к тому, чтобы найти
        последний клик пользователя по партнеской ссылке в рамках окна аттрибуции

        СМЫСЛ АЛГОРИТМА:
        - сортируем записи по времени в обратном порядке
        - итерируемся по отсортированному массиву, сохраняя индексы сейлов в отдельном объекте. Каждый элемент массива
        проверяем на соответствие реф-ссылке и определяем наша она или конкурентов. При любом из совпадений удаляем
        найденный сейл из списка кандидатов, если ссылка наша - проверяем укладывается ли она в окно аттрибуции и если
        да - сохраняем в результирующий список. Таким образом после сортировки сложность алгоритма будет линейная

        ВАЖНО! чисто теоретически возможная ситуация когда datetime разных реф ссылок равны. Тогда возникнет неопределенное
        поведение. Однако на практике такое почти невозможно, так что можно этой опасностью пренебречь

        :param log_records: несортированный список записей в логе
        :return: список записей в логе с продажами, совершенными по "нашей" ссылке
        """
        # --- Init ---
        result: T.List[LogRecord] = []
        log_records = sorted(log_records, key=lambda x: x.created_at, reverse=True)

        # --- Main Algorithm - O(n) ---
        sales_candidates: T.Dict[str, T.List[int]] = {}

        for index, record in enumerate(log_records):
            # write our sales candidates
            if record.location == SALE_LOCATION:
                sales_candidates[record.id] = [index] if sales_candidates.get(record.id) is None \
                    else [*sales_candidates[record.id], index]
                continue  # we not parse referer, cause situation with direct afflink on checkout is impossible

            # check ref links
            if record.referer is not None:
                is_affiliate_link, is_our_link = handle_ref_link(record.referer)

                if is_affiliate_link and sales_candidates.get(record.id):
                    #  delete from sales cause log_records is sorted by time and in any way
                    #  this sales could not belong to us
                    sales: T.List[int] = sales_candidates.pop(record.id)

                    # if ref is ours - check that we deal them within attribution window
                    if is_our_link:
                        for sale_index in sales:
                            seconds_diff = (log_records[sale_index].created_at - record.created_at).total_seconds()

                            if seconds_diff < ATTRIBUTION_WINDOW * 3600:
                                result.append(log_records[sale_index])

        return result


# --- TESTS ---
datetime_format = "%Y-%m-%d %H:%M:%S"


class TestWithAttributionSolution:
    @classmethod
    def get_record_ids(cls, records: T.List[LogRecord]) -> T.List[str]:
        return [record.id for record in records]

    def test_simple(self):
        input_data = [
            LogRecord(
                id="1",
                created_at=datetime.strptime("2019-10-01 09:00:00", datetime_format),
                location=SALE_LOCATION,
                referer=None
            ),
            LogRecord(
                id="1",
                created_at=datetime.strptime("2019-10-01 08:00:00", datetime_format),
                location="https://shop.com",
                referer="https://referal.ours.com/?ref=123hexcode"
            )
        ]

        assert self.get_record_ids(Solution.with_attribution_approach(input_data)) == ["1"]

    def test_wrong_init_order(self):
        input_data = [
            LogRecord(
                id="1",
                created_at=datetime.strptime("2019-10-01 08:00:00", datetime_format),
                location="https://shop.com",
                referer="https://referal.ours.com/?ref=123hexcode"
            ),
            LogRecord(
                id="1",
                created_at=datetime.strptime("2019-10-01 09:00:00", datetime_format),
                location=SALE_LOCATION,
                referer=None
            )
        ]

        assert self.get_record_ids(Solution.with_attribution_approach(input_data)) == ["1"]

    def test_multiple_sale_one_within_attribution_window(self):
        input_data = [
            LogRecord(
                id="1",
                created_at=datetime.strptime("2019-10-02 09:00:00", datetime_format),
                location=SALE_LOCATION,
                referer=None
            ),
            LogRecord(
                id="1",
                created_at=datetime.strptime("2019-10-02 08:00:00", datetime_format),
                location=SALE_LOCATION,
                referer="https://shop.com/cart"
            ),
            LogRecord(
                id="1",
                created_at=datetime.strptime("2019-10-01 08:10:00", datetime_format),
                location="https://shop.com",
                referer="https://referal.ours.com/?ref=123hexcode"
            )
        ]

        assert self.get_record_ids(Solution.with_attribution_approach(input_data)) == ["1"]

    def test_competitor_wins(self):
        input_data = [
            LogRecord(
                id="1",
                created_at=datetime.strptime("2019-10-02 08:00:00", datetime_format),
                location=SALE_LOCATION,
                referer="https://shop.com/cart"
            ),
            LogRecord(
                id="1",
                created_at=datetime.strptime("2019-10-01 09:10:00", datetime_format),
                location="https://shop.com",
                referer="http://theirs1.com/?ref=123hexcode"
            ),
            LogRecord(
                id="1",
                created_at=datetime.strptime("2019-10-01 09:00:00", datetime_format),
                location="https://shop.com",
                referer="https://referal.ours.com/?ref=123hexcode"
            )
        ]

        assert self.get_record_ids(Solution.with_attribution_approach(input_data)) == []

    def test_no_winners(self):
        input_data = [
            LogRecord(
                id="1",
                created_at=datetime.strptime("2019-10-02 08:21:00", datetime_format),
                location=SALE_LOCATION,
                referer="https://shop.com/cart"
            ),
            LogRecord(
                id="2",
                created_at=datetime.strptime("2019-10-02 08:20:00", datetime_format),
                location=SALE_LOCATION,
                referer="https://shop.com/cart"
            ),
            LogRecord(
                id="1",
                created_at=datetime.strptime("2019-10-02 08:00:00", datetime_format),
                location="https://shop.com/cart",
                referer="https://yandex.ru"
            )
        ]

        assert self.get_record_ids(Solution.with_attribution_approach(input_data)) == []
