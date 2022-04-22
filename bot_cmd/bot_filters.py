import json
import os
import requests
from typing import List
from dotenv import load_dotenv
from loguru import logger
import datetime
load_dotenv()

date_1 = datetime.date.today() + datetime.timedelta(days=1)
date_2 = date_1 + + datetime.timedelta(days=1)


@logger.catch
def best_deal(hotel_cnt: str, city_id: str, distance: str, price: str) -> List:
    """
    :param price: принимает строковое значение предельного расстояния от центра города до отеля в км/милях
    :param distance: принимает строковое значение диапазона цен
    :param city_id: принимает строковое значение id искомого города
    :param hotel_cnt: принимает строковое значение количества искомых отелей
    :return: возвращает список отелей в искомом городе по указанным параметрам
    """

    x_rapid_key = os.getenv('RapidAPI_Key')
    url = "https://hotels4.p.rapidapi.com/properties/list"

    querystring = {"destinationId": city_id, "pageNumber": "1", "pageSize": '100',
                   "checkIn": date_1, "checkOut": date_2, "adults1": "1",
                   "sortOrder": "PRICE",  "locale": "ru_RU"}

    headers = {
        'x-rapidapi-host': "hotels4.p.rapidapi.com",
        'x-rapidapi-key': x_rapid_key
        }

    try:
        response = requests.request("GET", url, headers=headers, params=querystring, timeout=10)
    except requests.exceptions.RequestException as err:
        raise requests.RequestException(f'req_err: {err}')

    data = json.loads(response.text)

    price_low = float(price.split()[0])
    price_high = float(price.split()[1])
    if price_low > price_high:
        price_low, price_high = price_high, price_low

    # with open(f'{city_id}_HOTELS.json', 'w', encoding='utf-8') as file:
    #     json.dump(data, file, indent=4)
    #
    # with open(f'{city_id}_HOTELS.json', 'r', encoding='utf-8') as file:
    #     data = json.load(file)

    hotel_list = data["data"]["body"]["searchResults"]["results"]

    hotel_list_mod = []
    res_count = 0

    for elem in hotel_list:
        user_dist = float(distance.replace(',', '.'))
        hotel_dist = float(elem.get("landmarks", {})[0].get("distance", '9999999').split()[0].replace(',', '.'))
        hotel_price = float(elem.get("ratePlan", {}).get("price", {}).get("current", '9999')[1:])

        if user_dist >= hotel_dist and price_low <= hotel_price <= price_high:

            info_appending(elem, hotel_list_mod)

            res_count += 1
            if res_count >= int(hotel_cnt):
                break

    return hotel_list_mod


@logger.catch
def low_high_price(hotel_cnt: str, city_id: str, cmd: str) -> List:
    """
    :param cmd: принимает строковое значение команды, запрошенной пользователем
    :param city_id: принимает строковое значение id искомого города
    :param hotel_cnt: принимает строковое значение количества искомых отелей
    :return: возвращает список отелей в искомом городе с мин ценой за ночь
    """

    x_rapid_key = os.getenv('RapidAPI_Key')
    url = "https://hotels4.p.rapidapi.com/properties/list"

    sort_order = "PRICE_HIGHEST_FIRST"
    if cmd == 'lowprice':
        sort_order = "PRICE"
    querystring = {"destinationId": city_id, "pageNumber": "1", "pageSize": hotel_cnt,
                   "checkIn": date_1, "checkOut": date_2, "adults1": "1",
                   "sortOrder": sort_order, "locate": "ru_RU"}

    headers = {
        'x-rapidapi-host': "hotels4.p.rapidapi.com",
        'x-rapidapi-key': x_rapid_key
        }

    try:
        response = requests.request("GET", url, headers=headers, params=querystring, timeout=10)
    except requests.exceptions.RequestException as err:
        raise requests.RequestException(f'req_err: {err}')

    data = json.loads(response.text)

    # with open(f'{city_id}_HOTELS.json', 'w', encoding='utf-8') as file:
    #     json.dump(data, file, indent=4)
    #
    # with open(f'{city_id}_HOTELS.json', 'r', encoding='utf-8') as file:
    #     data = json.load(file)

    hotel_list = data["data"]["body"]["searchResults"]["results"]

    hotel_list_mod = []

    for elem in hotel_list:
        info_appending(elem, hotel_list_mod)

    return hotel_list_mod


@logger.catch
def info_appending(elem_dict: dict, hotel_list_mod: List) -> List:
    """
    Функция проверяет словарь на наличие значений в необходимых ключах и запалняет ими список
    :param elem_dict: принимает на вход вложенные словари с информацией по отелю
    :param hotel_list_mod: принимает на вход список, который заполняется необходимыми данными по отелям
    :return:
    """

    no_info = 'n/a, check web-site'
    hotel_list_mod.append({
        'id': elem_dict.get('id', no_info),
        'Название отеля': elem_dict.get('name', no_info),
        'web-site': 'hotels.com/ho' + str(elem_dict.get('id', 0)),
        'Количество звёзд': elem_dict.get('starRating', no_info),
        'Пользовательский рейтинг': elem_dict.get("guestReviews", {}).get("unformattedRating", no_info),
        'Адрес': elem_dict.get("address", {}).get("streetAddress", no_info),
        'Расстояние до центра': elem_dict.get("landmarks", {})[0].get("distance", no_info),
        'Текущая стоимость за ночь': elem_dict.get("ratePlan", {}).get("price", {}).get("current", no_info),
    })

    return hotel_list_mod
