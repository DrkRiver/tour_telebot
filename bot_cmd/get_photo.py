import os
import requests
from dotenv import load_dotenv
load_dotenv()

X_RAPID_KEY = os.getenv('RapidAPI_Key')


def get_pict_url(hotel_id: str, pict_cnt: int) -> list:
    url = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"

    querystring = {"id": hotel_id}

    headers = {
        'x-rapidapi-host': "hotels4.p.rapidapi.com",
        'x-rapidapi-key': X_RAPID_KEY
    }
    response = requests.request("GET", url, headers=headers, params=querystring, timeout=10)

    data = response.json()
    pics: list = [pic_url['baseUrl'].replace('{size}', 'b') for pic_url in data['hotelImages'][:pict_cnt]]

    return pics


# print(get_pict_url('540688', 3))