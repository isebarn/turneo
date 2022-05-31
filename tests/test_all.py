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
