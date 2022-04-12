import json
import os
import requests
from typing import List
from dotenv import load_dotenv
load_dotenv()


def best_deal(hotel_cnt: str, city_id: str, distance: str, price: str) -> List:
    """
    :param price: принимает строковое значение предельного расстояния от центра городо до отеля в милях
    :param distance: принимает строковое значение диапазона цен
    :param city_id: принимает строковое значение id искомого города
    :param hotel_cnt: принимает строковое значение количества искомых отелей
    :return: возвращает список отелей в искомом городе по указанным параметрам за ночь
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

    hotel_list_mod = []
    res_count = 0

    for elem in hotel_list:
        user_dist = float(distance.replace(',', '.'))
        hotel_dist = -0.1
        hotel_price = -0.1
        if elem["landmarks"][0]["distance"]:
            hotel_dist = float(elem["landmarks"][0]["distance"].replace(',', '.')[:-5])
        if elem["ratePlan"]["price"]["exactCurrent"]:
            hotel_price = elem["ratePlan"]["price"]["exactCurrent"]

        if user_dist >= hotel_dist and price_low <= hotel_price <= price_high:

            info_appending(elem, hotel_list_mod)

            res_count += 1
            if res_count >= int(hotel_cnt):
                break

    return hotel_list_mod


def info_appending(elem_dict: dict, hotel_list_mod: List) -> List:
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
        '\nid': val_list[0],
        'name': val_list[1],
        'web-site': 'hotels.com/ho' + str(val_list[0]),
        'star rating': val_list[6],
        'rating': val_list[2],
        'address': val_list[3],
        'distance': val_list[4],
        'cur price': val_list[5],
    })

    return hotel_list_mod


print(best_deal('2', '549499', '10', '4 50'))
