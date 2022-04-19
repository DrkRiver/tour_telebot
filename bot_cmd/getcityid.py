import requests
import json
import os
from dotenv import load_dotenv
from typing import Tuple
from loguru import logger
load_dotenv()


@logger.catch
def get_city_id(city: str) -> Tuple or bool:
    """

    :param city: принимает строковое значение названия искомого города
    :return: возвращает кортеж из строкового значения ID искомого города и его корректного названия,
             если введенный пользователем город не найден - возвращает булевое значение Ложь
    """
    x_rapid_key = os.getenv('RapidAPI_Key')
    url = "https://hotels4.p.rapidapi.com/locations/v2/search"

    querystring = {"query": city, "locate": "ru_RU"}
    headers = {
        'x-rapidapi-host': "hotels4.p.rapidapi.com",
        'x-rapidapi-key': x_rapid_key
    }

    try:
        response = requests.request("GET", url, headers=headers, params=querystring, timeout=10)
    except requests.exceptions.RequestException as e:
        raise requests.RequestException(f'req_err: {e}')

    data = json.loads(response.text)

    # with open(f'{city}.json', 'w') as file:
    #     json.dump(data, file, indent=4)
    #
    # with open(f'{city}.json', 'r') as file:
    #     data = json.load(file)

    try:
        city_reg = data["suggestions"][0]["entities"][0]["caption"]
        if city_reg.startswith('<'):
            city_reg = city_reg[city_reg.rfind(",") + 1:]
            city_reg = data["suggestions"][0]["entities"][0]["name"] + ',' + city_reg
        elif city_reg.endswith('>'):
            city_reg = city_reg[:city_reg.rfind(",") + 1]
            city_reg = city_reg[:-1]
        else:
            city_reg = data["suggestions"][0]["entities"][0]["name"]
        # ud.add_info_to_db('city', data["suggestions"][0]["entities"][0]["caption"])
        return data["suggestions"][0]["entities"][0]["destinationId"], city_reg

    except IndexError:
        logger.error(f'Запрос по городу {city} не дал результата')
        return False
