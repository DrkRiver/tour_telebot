import requests
import json
import os
from dotenv import load_dotenv
from typing import Tuple
from loguru import logger
import re
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

    querystring = {"query": city}
    headers = {
        'x-rapidapi-host': "hotels4.p.rapidapi.com",
        'x-rapidapi-key': x_rapid_key
    }

    try:
        response = requests.request("GET", url, headers=headers, params=querystring, timeout=10)
    except requests.exceptions.RequestException as err:
        raise requests.RequestException(f'req_err: {err}')

    data = json.loads(response.text)

    try:
        city_reg = re.sub(r"(</span>)", '', re.sub(
            r"(<span class='highlighted'>)", '', data["suggestions"][0]["entities"][0]["caption"]))
        return data["suggestions"][0]["entities"][0]["destinationId"], city_reg

    except IndexError:
        logger.error(f'Запрос по городу {city} не дал результата')
        return False
