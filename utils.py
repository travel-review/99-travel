import typing
import random
import requests
from pymongo import MongoClient
from faker import Faker

# 더미데이터를 만들어주는 코드

factory = Faker()
continents = tuple(['seoul', 'europe', 'america', 'east_asia', 'southeast_asi', 'oceania', 'ect'])  # TODO: ect ...?

# 더미데이터 제공 url
_FALLBACK_URL = 'https://t2.gstatic.com/images?q=tbn:ANd9GcQHjpQ16ZIupZR7ENzIyyXJr4v_pEWzML9EFy1SqyuwTgpfP_YnH8r-Mq96CypOs-Vk0eWHwWEIB-gy1uJSDp9kfw'

client = MongoClient('127.0.0.1')
db = client.my_sparta

# db.places.insert_one(
#     {
#         'title': '장소',
#         'description': '설명',
#         'userId': '유저의 아이디',
#         'img_url': 'https://t2.gstatic.com/images?q=tbn:ANd9GcQHjpQ16ZIupZR7ENzIyyXJr4v_pEWzML9EFy1SqyuwTgpfP_YnH8r-Mq96CypOs-Vk0eWHwWEIB-gy1uJSDp9kfw',
#         'like': [],
#         'continent': 'europe' 지정된 형식으로 받아야 합니다.
#     })

## 더미데이터를 n개만큼 삽입합니다.
def insert_fake_places(n):
    try:
        places = _gen_fake_place_dicts(n)
        db.places.insert_many(places)
    except Exception as err:
        print("mongodb fake insert 초기화 잘 안됨")
        print(err)
        # raise err


# 더미데이터의 db에 들어갈 데이터를 생성합니다.
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

# 더미데이터를 외부 api를 이용하여 뽑아옵니다.
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
