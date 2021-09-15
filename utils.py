import json
import typing
import random
from urllib.request import urlopen

import requests

from app import db
from faker import Faker

factory = Faker()
continents = tuple(['seoul', 'europe', 'america', 'east_asia', 'southeast_asi', 'oceania', 'ect'])  # TODO: ect ...?

_FALLBACK_URL = 'https://t2.gstatic.com/images?q=tbn:ANd9GcQHjpQ16ZIupZR7ENzIyyXJr4v_pEWzML9EFy1SqyuwTgpfP_YnH8r-Mq96CypOs-Vk0eWHwWEIB-gy1uJSDp9kfw'


def insert_fake_places(n):
    try:
        places = _gen_fake_place_dicts(n)
        db.places.insert_many(places)
    except Exception as err:
        print("mongodb fake insert 초기화 잘 안됨")
        print(err)
        # raise err


def _gen_fake_place_dicts(n) -> typing.List:
    # n = # of places to generate
    results = []
    for _ in range(n):
        continent = random.choice(continents)
        place = {
            'title': factory.city(),
            'description': factory.sentence(),
            'userId': factory.random_int(min=1, max=999),
            'img_url': _get_random_place_image(continent),
            'like': ['rrrr'],
            'continent': continent
        }
        results.append(place)
    return results


def _get_random_place_image(continent_name):
    base_url = "https://source.unsplash.com"
    base_img_size = '210x132'
    base_keywords = f"travel,{continent_name}"
    request_url = f"{base_url}/{base_img_size}/?{base_keywords}"
    r = requests.get(request_url)
    try:
        img_url = r.url
    except Exception as err:
        img_url = _FALLBACK_URL
    return img_url
