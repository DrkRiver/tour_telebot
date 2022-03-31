import json
import os
import requests
from typing import List, Any
from dotenv import load_dotenv
load_dotenv()


def low_price(hotel_cnt: str, city_id: str) -> List:
    """
    :param city_id: принимает строковое значение id искомого города
    :param hotel_cnt: принимает строковое значение количества искомых отелей
    :return: возвращает список отелей в искомом городе с мин ценой за ночь
    """

    # city_id = get_city_id(city)

    X_RAPID_KEY = os.getenv('RapidAPI_Key')
    url = "https://hotels4.p.rapidapi.com/properties/list"

    querystring = {"destinationId": city_id, "pageNumber": "1", "pageSize": hotel_cnt,
                   "checkIn": "2022-06-08", "checkOut": "2022-06-09", "adults1": "1",
                   "sortOrder": "PRICE"}

    headers = {
        'x-rapidapi-host': "hotels4.p.rapidapi.com",
        'x-rapidapi-key': X_RAPID_KEY
        }

    response = requests.request("GET", url, headers=headers, params=querystring)
    data = json.loads(response.text)

    # with open(f'{city}_HOTELS.json', 'w', encoding='utf-8') as file:
    #     json.dump(data, file, indent=4)
    #
    # with open(f'{city}_HOTELS.json', 'r', encoding='utf-8') as file:
    #     data = json.load(file)

    hotel_list = data["data"]["body"]["searchResults"]["results"]

    # with open(f'{city}_TEST_TEST.json', 'w', encoding='utf-8') as file:
    #     json.dump(hotel_list, file, indent=4)

    hotel_list_mod = []

    for elem in hotel_list:
        try:
            name = elem["name"]
        except KeyError:
            name = 'N/A'
        try:
            addr = elem["address"]["streetAddress"]
        except KeyError:
            addr = 'N/A'
        try:
            dist = elem["landmarks"][0]["distance"]
        except KeyError:
            dist = 'N/A'
        try:
            cur_price = elem["ratePlan"]["price"]["current"]
        except KeyError:
            cur_price = 'N/A'

        hotel_list_mod.append({
                    'id': elem['id'],
                    'name': name,
                    'address': addr,
                    'distance': dist,
                    'cur price': cur_price,
        })
    print(hotel_list_mod)

    return hotel_list_mod


