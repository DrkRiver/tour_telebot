import json
import os
import requests
from typing import List, Any
from dotenv import load_dotenv
load_dotenv()


def best_deal(hotel_cnt: str, city_id: str, distance: str, price: str) -> List:
    """
    :param city_id: принимает строковое значение id искомого города
    :param hotel_cnt: принимает строковое значение количества искомых отелей
    :return: возвращает список отелей в искомом городе с мин ценой за ночь
    """

    x_rapid_key = os.getenv('RapidAPI_Key')
    url = "https://hotels4.p.rapidapi.com/properties/list"

    querystring = {"destinationId": city_id, "pageNumber": "1", "pageSize": '100',
                   "checkIn": "2022-06-08", "checkOut": "2022-06-09", "adults1": "1",
                   "sortOrder": "PRICE"}

    headers = {
        'x-rapidapi-host': "hotels4.p.rapidapi.com",
        'x-rapidapi-key': x_rapid_key
        }

    response = requests.request("GET", url, headers=headers, params=querystring)
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

    # with open(f'{city}_TEST_TEST.json', 'w', encoding='utf-8') as file:
    #     json.dump(hotel_list, file, indent=4)

    hotel_list_mod = []
    res_count = 0

    for elem in hotel_list:
        user_dist = float(distance.replace(',', '.'))
        try:
            hotel_dist = float(elem["landmarks"][0]["distance"].replace(',', '.')[:-5])
        except KeyError:
            hotel_dist = -0.1
        try:
            hotel_price = elem["ratePlan"]["price"]["exactCurrent"]
        except KeyError:
            hotel_price = -0.1

        if user_dist >= hotel_dist and price_low <= hotel_price <= price_high:

            try:
                name = elem["name"]
            except KeyError:
                name = 'N/A'
            try:
                star_rate = elem["starRating"]
            except KeyError:
                star_rate = 'N/A'
            try:
                rating = elem["guestReviews"]['unformattedRating']
            except KeyError:
                rating = 'N/A'
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
                        '\nid': elem['id'],
                        'name': name,
                        'star rating': star_rate,
                        'rating': rating,
                        'address': addr,
                        'distance': dist,
                        'cur price': cur_price,
            })
            res_count += 1
            if res_count >= int(hotel_cnt):
                break

    return hotel_list_mod


