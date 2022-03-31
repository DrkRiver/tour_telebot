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
    X_RAPID_KEY = os.getenv('RapidAPI_Key')
    url = "https://hotels4.p.rapidapi.com/locations/v2/search"

    querystring = {"query": city}

    headers = {
        'x-rapidapi-host': "hotels4.p.rapidapi.com",
        'x-rapidapi-key': X_RAPID_KEY
    }

    response = requests.request("GET", url, headers=headers, params=querystring)
    data = json.loads(response.text)

    # with open(f'{city}.json', 'w') as file:
    #     json.dump(data, file, indent=4)
    #
    # with open(f'{city}.json', 'r') as file:
    #     data = json.load(file)

    # print(data["suggestions"][0]["entities"][0]["destinationId"])
    return data["suggestions"][0]["entities"][0]["destinationId"]

