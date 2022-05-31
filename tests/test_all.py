import pytest
import requests

url = "http://127.0.0.1:5000/api/{}"


def delete(table):
    response = requests.get(url.format("{}".format(table)))
    items = response.json()

    for item in items:
        requests.delete(url.format("{}/{}".format(table, item["id"])))


def clean():
    for item in ["experiences", "rates", "bookings"]:
        delete(item)


def get(endpoint):
    response = requests.get(url.format(endpoint))
    return response.json()


def post(endpoint, data):
    response = requests.post(url.format(endpoint), json=data)
    return response.json()


def patch(endpoint, data):
    response = requests.patch(url.format(endpoint), json=data)
    return response.json()


def put(endpoint, data):
    response = requests.put(url.format(endpoint), json=data)
    return response.json()


def assert_count(query, count):
    return len(get(query)) == count


def return_one(query):
    return get(query)[0]


# test post + get
# test post + get + filter
# test post + get + limit
# test post + get + skip
# test post + get + filter + skip + limit
# test patch + get
# test put + get
def test_experience():
    clean()

    exp_1 = post("experiences", {"name": "exp_1", "cutOffTime": 10})
    assert assert_count("experiences", 1)

    exp_2 = post("experiences", {"name": "exp_2", "cutOffTime": 20})
    assert assert_count("experiences", 2)
    assert assert_count("experiences?name=exp_2", 1)
    assert assert_count("experiences?cutOffTime__gt=15", 1)
    assert assert_count("experiences?cutOffTime__gt=19", 1)
    assert assert_count("experiences?cutOffTime__gte=19", 1)
    assert assert_count("experiences?cutOffTime__gte=20", 1)
    assert assert_count("experiences?cutOffTime__gt=20", 0)
    assert assert_count("experiences?cutOffTime__lt=20", 1)
    assert assert_count("experiences?cutOffTime__lte=20", 2)

    exp_3 = post(
        "experiences",
        {
            "name": "exp_3",
            "cutOffTime": 20,
            "organizer": {"name": "Jack", "organizerType": "Cars"},
        },
    )
    assert assert_count("experiences?", 3)
    assert assert_count("experiences?organizer__exists", 1)
    assert assert_count("experiences?organizer__name=Jack", 1)
    assert assert_count(
        "experiences?organizer__name=Jack&organizer__organizerType=Cars", 1
    )
    assert "organizer" in return_one("experiences?organizer__exists")
    assert "name" in return_one("experiences?organizer__exists")["organizer"]
    assert "organizerType" in return_one("experiences?organizer__exists")["organizer"]

    exp_4 = post(
        "experiences",
        {
            "name": "exp_4",
            "cutOffTime": 20,
            "organizer": {"name": "John", "organizerType": "Boats"},
        },
    )
    assert assert_count("experiences?", 4)
    assert assert_count("experiences?$limit=2", 2)
    assert assert_count("experiences?$skip=1", 3)
    assert assert_count("experiences?organizer__exists", 2)
    assert assert_count("experiences?$limit=1&organizer__exists", 1)
    assert assert_count("experiences?$skip=1&organizer__exists", 1)
    assert assert_count("experiences?organizer__name=Jack", 1)
    assert "organizer" in return_one("experiences?organizer__name=Jack")
    assert "name" in return_one("experiences?organizer__name=Jack")["organizer"]
    assert return_one("experiences?organizer__name=Jack")["organizer"]["name"] == "Jack"
    assert (
        "organizerType" in return_one("experiences?organizer__name=Jack")["organizer"]
    )

    exp_5 = post(
        "experiences",
        {
            "name": "exp_5",
            "cutOffTime": 20,
            "organizer": {"name": "John", "organizerType": "Boats"},
            "images": [
                {
                    "urlHigh": "High_1",
                    "urlLow": "Low_1",
                },
                {
                    "urlHigh": "High_2",
                    "urlLow": "Low_2",
                },
            ],
        },
    )

    assert assert_count("experiences?", 5)
    assert assert_count("experiences?images__exists", 5)
    assert assert_count("experiences?images__ne=[]", 1)
    assert assert_count("experiences?images__0__urlHigh=High_1", 1)
    assert assert_count("experiences?images__1__urlHigh=High_2", 1)
    assert get("experiences/{}".format(exp_5["id"]))
    assert "images" in get("experiences/{}".format(exp_5["id"]))
    assert get("experiences/{}".format(exp_5["id"]))["images"][0]["urlHigh"]
    assert get("experiences/{}".format(exp_5["id"]))["images"][0]["urlLow"]
    assert get("experiences/{}".format(exp_5["id"]))["images"][1]["urlHigh"]
    assert get("experiences/{}".format(exp_5["id"]))["images"][1]["urlLow"]


# test post + get
# test post + get check sort
# test post + get + manual sort
# test post + get + sort two
def test_experience_default_sort():
    clean()

    exp_1 = post(
        "experiences", {"name": "exp_1", "rating": {"score": 4.5, "reviewsCount": 1200}}
    )
    exp_2 = post(
        "experiences", {"name": "exp_2", "rating": {"score": 4.2, "reviewsCount": 100}}
    )
    exp_3 = post(
        "experiences", {"name": "exp_3", "rating": {"score": 4.8, "reviewsCount": 1000}}
    )
    exp_4 = post(
        "experiences", {"name": "exp_4", "rating": {"score": 3.8, "reviewsCount": 32}}
    )
    assert assert_count("experiences", 4)

    assert get("experiences?$sort=rating__score")[0]["id"] == exp_4["id"]
    assert get("experiences?$sort=rating__score")[1]["id"] == exp_2["id"]
    assert get("experiences?$sort=rating__score")[2]["id"] == exp_1["id"]
    assert get("experiences?$sort=rating__score")[3]["id"] == exp_3["id"]

    exp_5 = post(
        "experiences", {"name": "exp_5", "rating": {"score": 4.2, "reviewsCount": 101}}
    )

    exp_6 = post(
        "experiences", {"name": "exp_6", "rating": {"score": 4.5, "reviewsCount": 50}}
    )

    exp_7 = post(
        "experiences", {"name": "exp_7", "rating": {"score": 4.5, "reviewsCount": 5000}}
    )

    sort = "experiences?$sort=-rating__score,-rating__reviewsCount"
    assert get(sort)[0]["id"] == exp_3["id"]
    assert get(sort)[1]["id"] == exp_7["id"]
    assert get(sort)[2]["id"] == exp_1["id"]
    assert get(sort)[3]["id"] == exp_6["id"]
    assert get(sort)[4]["id"] == exp_5["id"]
    assert get(sort)[5]["id"] == exp_2["id"]
    assert get(sort)[6]["id"] == exp_4["id"]

    sort = "experiences?$sort=None"
    assert get(sort)[0]["id"] == exp_1["id"]
    assert get(sort)[1]["id"] == exp_2["id"]
    assert get(sort)[2]["id"] == exp_3["id"]
    assert get(sort)[3]["id"] == exp_4["id"]
    assert get(sort)[4]["id"] == exp_5["id"]
    assert get(sort)[5]["id"] == exp_6["id"]
    assert get(sort)[6]["id"] == exp_7["id"]


# test post + get
# test post + get check sort
# test post + get + manual sort
# test post + get + sort two
def test_experience_default_values():
    clean()

    exp_1 = post("experiences", {"name": "exp_1"})
    exp_2 = post("experiences", {"name": "exp_2", "status": "active"})
    assert assert_count("experiences", 2)

    assert get("experiences/{}".format(exp_1["id"]))["status"] == "draft"
    assert get("experiences/{}".format(exp_2["id"]))["status"] == "active"

    patch("experiences/{}".format(exp_1["id"]), {"status": "active"})
    assert assert_count("experiences?status=active", 2)
