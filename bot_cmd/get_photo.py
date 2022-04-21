import os
import requests
from dotenv import load_dotenv
from loguru import logger
load_dotenv()

X_RAPID_KEY = os.getenv('RapidAPI_Key')


@logger.catch
def get_pict_url(hotel_id: str, pict_cnt: int) -> list:
    """
    Функция по получения ссылок на фотографии к найденному отелю
    :param hotel_id: принимает строковое значение id найденного отеля
    :param pict_cnt: принимает целочисленное значение количества фотографий
    :return: возвращает список из ссылок на фотографии
    """
    url = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"

    querystring = {"id": hotel_id}

    headers = {
        'x-rapidapi-host': "hotels4.p.rapidapi.com",
        'x-rapidapi-key': X_RAPID_KEY
    }
    if int(pict_cnt) > 0:
        try:
            response = requests.request("GET", url, headers=headers, params=querystring, timeout=10)
        except requests.exceptions.RequestException as err:
            raise requests.RequestException(f'req_err: {err}')

        try:
            data = response.json()
            pics: list = [pic_url['baseUrl'].replace('{size}', 'b') for pic_url in data['hotelImages'][:pict_cnt]]
        except Exception as err:
            raise Exception(f'Ошибка парсинга фото: {err}')

        return pics
