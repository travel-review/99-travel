import typing

from app import db
from faker import Faker

Faker.seed(1234)
factory = Faker()

continent = ['seoul', 'eu', 'af', 'asia']

def insert_fake_places(n):
    try:
        places = _gen_fake_place_dicts(n)
        db.places.insert_many(places)
    except Exception as err:
        print("mongodb fake insert 초기화 잘 안됨")
        print(err)


def _gen_fake_place_dicts(n) -> typing.List:
    # n = # of places to generate
    results = []
    for _ in range(n):
        place = {
            'title': factory.city(),
            'description': factory.text(),
            'userId': factory.random_int(),
            'img_url': factory.image_url(), # TODO: img size 맞추기
            'like': ['rrrr'],
            'continent': random.choice(continent)
        }
        results.append(place)
    return results
