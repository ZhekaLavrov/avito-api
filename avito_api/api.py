from datetime import date
from typing import Literal

import requests

from avito_api.rest_types import AccessToken, AutoloadItemInfo, UserInfoSelf, ItemStatsShallow, ItemStatsShallowDay, \
    ItemStatsShallowWeek, ItemStatsShallowMonth, Ok
from avito_api.exceptions import Error


class AvitoApi:
    def __init__(self, client_id: str, client_secret: str):
        """

        :param client_id:
        :param client_secret:
        """
        self.__client_id = client_id
        self.__client_secret = client_secret

        self._access_token = self.get_access_token()
        self.__access_token = self._access_token.access_token

        self.user_info_self = self.get_user_info_self()
        self.email = self.user_info_self.email
        self.id = self.user_info_self.id
        self.name = self.user_info_self.name
        self.phone = self.user_info_self.phone
        self.profile_url = self.user_info_self.profile_url

    def __get_access_token(self) -> dict:
        """
        Получения временного ключа для авторизации.
        https://developers.avito.ru/api-catalog/auth/documentation#operation/getAccessToken
        :return:
        """
        url = 'https://api.avito.ru/token/'
        grant_type = "client_credentials"
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
        }

        data = f'grant_type={grant_type}&client_id={self.__client_id}&client_secret={self.__client_secret}'

        response = requests.post(url, headers=headers, data=data)
        data = response.json()
        return data

    def get_access_token(self) -> AccessToken:
        """
        Получения временного ключа для авторизации.
        https://developers.avito.ru/api-catalog/auth/documentation#operation/getAccessToken
        :return:
        """
        data = self.__get_access_token()
        if data.get("error"):
            raise Error(data.get("error", ''), data.get("error_description", ''))
        access_token = AccessToken.parse_obj(data)
        return access_token

    def __get_user_info_self(self) -> dict:
        """
        Возвращает идентификатор пользователя и его регистрационные данные.
        https://developers.avito.ru/api-catalog/user/documentation#operation/getUserInfoSelf
        :return:
        """
        url = "https://api.avito.ru/core/v1/accounts/self"
        headers = {
            'Authorization': f"Bearer {self.__access_token}",
            'Content-Type': 'application/json',
        }
        response = requests.get(url=url, headers=headers)
        data = response.json()
        return data

    def get_user_info_self(self) -> UserInfoSelf:
        """
        Возвращает идентификатор пользователя и его регистрационные данные.
        https://developers.avito.ru/api-catalog/user/documentation#operation/getUserInfoSelf
        :return:
        """
        data = self.__get_user_info_self()
        if error := data.get("error"):
            raise Error(error.get('code'), error.get('message'))
        user_info_self = UserInfoSelf.parse_obj(data)
        return user_info_self

    def __get_autoload_items_info_v2(self, query: str) -> dict:
        """
        https://developers.avito.ru/api-catalog/autoload/documentation#operation/getAutoloadItemsInfoV2
        :param query: Идентификаторы объявлений из файла (параметр Id).
                      Формат значения: строка с идентификаторами, перечисленными через «,» или «|»
        :return: dict
            items: list[dict] - Список объявлений:
                ad_id: string - Идентификатор объявления из файла (параметр Id);
                avito_date_end:  string <date-time> Nullable - Дата окончания оплаченного
                                                               периода размещения объявления;
                avito_id: integer Nullable - Идентификатор объявления на Авито;
                avito_status: string Nullable - Статус объявления на Авито:
                    Enum: "active" "old" "blocked" "rejected" "archived" "removed":
                        active – Объявление активно;
                        old – Срок размещения объявления истёк;
                        blocked – Объявление заблокировано;
                        rejected – Объявление отклонено для исправления нарушений;
                        archived – Объявление находится в Архиве;
                        removed – Объявление удалено навсегда.
                fee_info: dict - Информация о списании за размещение объявления:
                    amount: integer Nullable - Сумма средств, списанных из кошелька
                                               за это объявление (передаётся, если type = single);
                    package_id: integer Nullable - ID пакета размещений, из которого было
                                                   списание за это объявление (передаётся, если type = package);
                    type: string - Способ оплаты:
                        Enum: "single" "package":
                            single – Оплата из кошелька;
                            package – Оплата из пакета размещений.
                messages list[dict] - Ошибки или предупреждения по объявлению:
                    code: integer - Код ошибки или предупреждения;
                    description: string - Описание ошибки или предупреждения;
                    title: string - Название ошибки или предупреждения;
                    type: string - Тип ошибки или предупреждения:
                        Enum: "error" "warning" "info" "alarm"
                            error – Критическая ошибка, которая влияет на выгрузку:
                                    объявление не редактируется или не публикуется;
                            warning – Некритическая ошибка, которая в будущем может
                                      повлиять на выгрузку или влияет сейчас на необязательный параметр;
                            alarm – Предупреждение, которое не влияет на выгрузку;
                            info – Информационное сообщение.
                    updated_at: string <date-time> - Дата актуальности ошибки или предупреждения.
                processing_time: string <date-time> Nullable - Дата и время последней обработки объявления;
                section: dict - Раздел отчёта, в котором находится объявление — то
                                есть результат обработки объявления в последней выгрузке:
                    slug: string - ID раздела;
                    title: string - Название раздела.
                url: string Nullable - Ссылка на объявление на Авито.
        :return example:
            {
              "items": [
                {
                  "ad_id": "string",
                  "avito_date_end": "2019-08-24T14:15:22Z",
                  "avito_id": 0,
                  "avito_status": "active",
                  "fee_info": {
                    "amount": 0,
                    "package_id": 0,
                    "type": "single"
                  },
                  "messages": [
                    {
                      "code": 0,
                      "description": "string",
                      "title": "string",
                      "type": "error",
                      "updated_at": "2019-08-24T14:15:22Z"
                    }
                  ],
                  "processing_time": "2019-08-24T14:15:22Z",
                  "section": {
                    "slug": "string",
                    "title": "string"
                  },
                  "url": "string"
                }
              ]
            }
        """
        url = 'https://api.avito.ru/autoload/v2/reports/items'
        params = {
            "query": query
        }
        headers = {
            'Authorization': f"Bearer {self.__access_token}",
            'Content-Type': 'application/json',
        }
        response = requests.get(url, headers=headers, params=params)
        data = response.json()
        return data

    def get_autoload_items_info_v2(self, ids: list[str]) -> list[AutoloadItemInfo]:
        """
        https://developers.avito.ru/api-catalog/autoload/documentation#operation/getAutoloadItemsInfoV2
        :param ids: список идентификаторов объявлений.
        :return: объект объявления.
        """
        query = ",".join(ids)
        data = self.__get_autoload_items_info_v2(query=query)
        if error := data.get("error"):
            raise Error(error.get('code'), error.get('message'))
        autoload_items_info = []
        for item in data.get("items", []):
            autoload_item_info = AutoloadItemInfo.parse_obj(item)
            autoload_items_info.append(autoload_item_info)
        return autoload_items_info

    def __item_stats_shallow(self, date_from: str, date_to: str, item_ids: list[int],
                             fields: list[Literal["views", "uniqViews", "contacts", "uniqContacts", "favorites",
                                                  "uniqFavorites"]] = None,
                             period_grouping: Literal["day", "week", "month"] = "day") -> dict:
        """
        https://developers.avito.ru/api-catalog/item/documentation#operation/itemStatsShallow
        :return:
        """
        if fields is None:
            fields = ["uniqViews", "uniqContacts", "uniqFavorites"]
        url = f"https://api.avito.ru/stats/v1/accounts/{self.id}/items"
        headers = {
            'Authorization': f"Bearer {self.__access_token}",
            'Content-Type': 'application/json',
        }
        params = {
            "dateFrom": date_from,
            "dateTo": date_to,
            "fields": fields,
            "itemIds": item_ids,
            "periodGrouping": period_grouping
        }
        response = requests.post(url=url, headers=headers, json=params)
        data = response.json()
        return data

    def items_stats_shallow(self, date_from: date, date_to: date, item_ids: list[int],
                            fields: list[Literal["views", "uniqViews", "contacts", "uniqContacts", "favorites",
                                                 "uniqFavorites"]] = None,
                            period_grouping: Literal[
                                "day", "week", "month"
                            ] = "day") -> list[ItemStatsShallowDay | ItemStatsShallowWeek | ItemStatsShallowMonth]:
        date_from = date_from.strftime("%Y-%m-%d")
        date_to = date_to.strftime("%Y-%m-%d")
        data = self.__item_stats_shallow(date_from, date_to, item_ids, fields, period_grouping)
        items = []
        if period_grouping == "day":
            for item in data.get('result', {}).get('items', []):
                items.append(ItemStatsShallowDay.parse_obj(item))
        elif period_grouping == "week":
            for item in data.get('result', {}).get('items', []):
                items.append(ItemStatsShallowWeek.parse_obj(item))
        elif period_grouping == "month":
            for item in data.get('result', {}).get('items', []):
                items.append(ItemStatsShallowMonth.parse_obj(item))
        return items

    def items_stats_shallow_day(self, date_from: date, date_to: date, item_ids: list[int],
                                fields: list[Literal["views", "uniqViews", "contacts", "uniqContacts", "favorites",
                                                     "uniqFavorites"]] = None) -> list[ItemStatsShallowDay]:
        items = self.items_stats_shallow(date_from, date_to, item_ids, fields, "day")
        return items

    def items_stats_shallow_week(self, date_from: date, date_to: date, item_ids: list[int],
                                 fields: list[Literal["views", "uniqViews", "contacts", "uniqContacts", "favorites",
                                                      "uniqFavorites"]] = None) -> list[ItemStatsShallowWeek]:
        items = self.items_stats_shallow(date_from, date_to, item_ids, fields, "week")
        return items

    def items_stats_shallow_month(self, date_from: date, date_to: date, item_ids: list[int],
                                  fields: list[Literal["views", "uniqViews", "contacts", "uniqContacts", "favorites",
                                                       "uniqFavorites"]] = None) -> list[ItemStatsShallowMonth]:
        items = self.items_stats_shallow(date_from, date_to, item_ids, fields, "month")
        return items

    def __post_webhook_v2(self, url: str) -> dict:
        """
        Включение V2 уведомлений
        https://developers.avito.ru/api-catalog/messenger/documentation#operation/postWebhookV2
        :param url: Url на который будут отправляться нотификации
        :return:
        """
        requests_url = 'https://api.avito.ru/messenger/v2/webhook'
        headers = {
            'Authorization': f"Bearer {self.__access_token}",
            'Content-Type': 'application/json',
        }
        response = requests.post(requests_url, headers=headers, json={"url": url})
        data = response.json()
        return data

    def post_webhook_v2(self, url: str) -> Ok:
        """
        Включение V2 уведомлений
        https://developers.avito.ru/api-catalog/messenger/documentation#operation/postWebhookV2
        :param url: Url на который будут отправляться нотификации
        :return:
        """
        ok = Ok.parse_obj(self.__post_webhook_v2(url))
        return ok

    def __post_webhook_unsubscribe(self, url: str) -> dict:
        """
        Отключение уведомлений
        https://developers.avito.ru/api-catalog/messenger/documentation#operation/postWebhookUnsubscribe
        :param url: Url, на который необходимо перестать слать уведомления.
        :return:
        """
        requests_url = 'https://api.avito.ru/messenger/v1/webhook/unsubscribe'
        headers = {
            'Authorization': f"Bearer {self.__access_token}",
            'Content-Type': 'application/json',
        }
        response = requests.post(requests_url, headers=headers, json={"url": url})
        data = response.json()
        return data

    def post_webhook_unsubscribe(self, url: str) -> Ok:
        """
        Отключение уведомлений
        https://developers.avito.ru/api-catalog/messenger/documentation#operation/postWebhookUnsubscribe
        :param url: Url, на который необходимо перестать слать уведомления.
        :return:
        """
        ok = Ok.parse_obj(self.__post_webhook_unsubscribe(url))
        return ok

    def __str__(self):
        return f"id: {self.id}"

    def __repr__(self):
        return self.__str__()
