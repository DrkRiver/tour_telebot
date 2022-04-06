import requests
import json
import os
from dotenv import load_dotenv
load_dotenv()


def get_city_id(city):
    """

    :param city: принимает строковое значение названия искомого города
    :return: возвращает строковое значение ID искомого города
    """
    x_rapid_key = os.getenv('RapidAPI_Key')
    url = "https://hotels4.p.rapidapi.com/locations/v2/search"

    querystring = {"query": city}

    headers = {
        'x-rapidapi-host': "hotels4.p.rapidapi.com",
        'x-rapidapi-key': x_rapid_key
    }

    response = requests.request("GET", url, headers=headers, params=querystring)
    data = json.loads(response.text)

    # with open(f'{city}.json', 'w') as file:
    #     json.dump(data, file, indent=4)
    #
    # with open(f'{city}.json', 'r') as file:
    #     data = json.load(file)

    try:
        city_reg = data["suggestions"][0]["entities"][0]["caption"]
        city_reg = city_reg[city_reg.rfind(",") + 1:]
        city_reg = data["suggestions"][0]["entities"][0]["name"] + ',' + city_reg
        # ud.add_info_to_db('city', data["suggestions"][0]["entities"][0]["caption"])
        return data["suggestions"][0]["entities"][0]["destinationId"], city_reg

    except IndexError:
        return False


# print(get_city_id('londo'))
