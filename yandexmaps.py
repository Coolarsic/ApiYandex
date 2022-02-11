
import requests


def get_coords(objname):
    api = '40d1649f-0493-4b70-98ba-98533de7710b'
    req = f'http://geocode-maps.yandex.ru/1.x/?apikey={api}&geocode={objname}&format=json'
    coords = requests.get(req).json()
    result = coords["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["boundedBy"]["Envelope"]["lowerCorner"]
    return result.split()