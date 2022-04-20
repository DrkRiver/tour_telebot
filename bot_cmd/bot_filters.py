import json
import os
import requests
from typing import List
from dotenv import load_dotenv
from loguru import logger
load_dotenv()


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
                   "checkIn": "2022-06-08", "checkOut": "2022-06-09", "adults1": "1",
                   "sortOrder": "PRICE",  "locale": "ru_RU"}

    headers = {
        'x-rapidapi-host': "hotels4.p.rapidapi.com",
        'x-rapidapi-key': x_rapid_key
        }

    try:
        response = requests.request("GET", url, headers=headers, params=querystring, timeout=10)
    except requests.exceptions.RequestException as e:
        raise requests.RequestException(f'req_err: {e}')

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
        hotel_dist = -0.1
        hotel_price = -0.1
        try:
            if elem["landmarks"][0]["distance"]:
                hotel_dist = float(elem["landmarks"][0]["distance"].replace(',', '.')[:-5])
            if elem["ratePlan"]["price"]["exactCurrent"]:
                hotel_price = elem["ratePlan"]["price"]["exactCurrent"]
        except (KeyError, ValueError):
            logger.error(f"По отелю с id {elem['id']} не заполнены ключевые поля. Отклонен.")
            continue

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
                   "checkIn": "2022-06-08", "checkOut": "2022-06-09", "adults1": "1",
                   "sortOrder": sort_order, "locate": "ru_RU"}

    headers = {
        'x-rapidapi-host': "hotels4.p.rapidapi.com",
        'x-rapidapi-key': x_rapid_key
        }

    try:
        response = requests.request("GET", url, headers=headers, params=querystring, timeout=10)
    except requests.exceptions.RequestException as e:
        raise requests.RequestException(f'req_err: {e}')

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
    teg_list = []
    teg_list.clear()
    teg_list = [elem_dict['id'], elem_dict["name"], elem_dict["guestReviews"]['unformattedRating'],
                elem_dict["address"]["streetAddress"], elem_dict["landmarks"][0]["distance"],
                elem_dict["ratePlan"]["price"]["current"], elem_dict["starRating"]]
    val_list = []
    for val in teg_list:
        if val:
            val_list.append(val)
        else:
            val_list.append('N/A')

    hotel_list_mod.append({
        'id': val_list[0],
        'Название отеля': val_list[1],
        'web-site': 'hotels.com/ho' + str(val_list[0]),
        'Количество звёзд': val_list[6],
        'Пользовательский рейтинг': val_list[2],
        'Адрес': val_list[3],
        'Расстояние до центра': val_list[4],
        'Текущая стоимость за ночь': val_list[5],
    })

    return hotel_list_mod
