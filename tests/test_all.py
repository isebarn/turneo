import pytest
import requests


def clean(url):
    response = requests.get(url.format("/api/experience"))
    experiences = response.json()

    for experience in experiences:
        requests.delete(url.format("/api/experience/{}".format(experience["id"])))

    response = requests.get(url.format("/api/rates"))
    rates = response.json()

    for rate in rates:
        requests.delete(url.format("/api/rates/{}".format(rate["id"])))


def get(endpoint, query=""):
    url = "http://127.0.0.1:5000/api/{}{}"
    response = requests.get(url.format(endpoint, query))
    return response.json()


def post(endpoint, data):
    url = "http://127.0.0.1:5000/api/{}"
    response = requests.post(url.format(endpoint), json=data)
    return response.json()


def patch(endpoint, data):
    url = "http://127.0.0.1:5000/api/{}"
    response = requests.patch(url.format(endpoint), json=data)
    return response.json()


def put(endpoint, data):
    url = "http://127.0.0.1:5000/api/{}"
    response = requests.put(url.format(endpoint), json=data)
    return response.json()


# test post + get
# test post + get + filter
# test post + get + limit
# test post + get + skip
# test post + get + filter + skip + limit
# test patch + get
# test put + get
def test_experience():
    url = "http://127.0.0.1:5000{}"
    clean(url)

    # Test post + get
    experience_1 = post("experience", {"status": "Active", "commission": 20})
    assert "id" in experience_1
    assert len(get("experience")) == 1

    # Test post + get + filter
    experience_2 = post("experience", {"status": "Active", "commission": 10})
    experience_3 = post("experience", {"status": "Inactive", "commission": 10})
    assert "id" in experience_2
    assert len(get("experience")) == 3
    assert len(get("experience?commission=10")) == 2
    assert len(get("experience?commission=10&status=Inactive")) == 1

    # test post + get + limit
    experience_4 = post("experience", {"status": "Inactive", "commission": 30})
    assert len(get("experience")) == 4
    assert len(get("experience?$limit=2")) == 2

    # test post + get + skip
    experience_5 = post("experience", {"status": "Inactive", "commission": 10})
    assert len(get("experience")) == 5
    assert len(get("experience?$skip=2")) == 3

    # test post + get + filter + skip + limit
    experience_6 = post("experience", {"status": "Inactive", "commission": 10})
    assert len(get("experience")) == 6
    assert len(get("experience?commission=10")) == 4
    assert len(get("experience?$skip=2&commission=10")) == 2
    assert len(get("experience?$skip=2&$limit=1&commission=10")) == 1

    # test patch + get
    assert (
        next(filter(lambda x: x["commission"] == 30, get("experience"))) == experience_4
    )
    experience_4_2 = patch("experience", {"id": experience_4["id"], "status": "Active"})
    assert experience_4_2["id"] == experience_4["id"]
    assert experience_4_2["commission"] == experience_4["commission"]
    assert experience_4_2["status"] != experience_4["status"]
    assert len(get("experience")) == 6
    assert len(get("experience?status=Active")) == 3

    # test put + get
    assert (
        next(filter(lambda x: x["commission"] == 30, get("experience")))
        == experience_4_2
    )
    experience_4_3 = put("experience", {"id": experience_4["id"], "status": "Active"})
    assert experience_4_3["id"] == experience_4["id"]
    assert "commission" not in experience_4_3
    assert experience_4_3["status"] == experience_4_2["status"]
    assert len(get("experience")) == 6
    assert len(get("experience?status=Active")) == 3


# test post(rate) + get
# test post(rate + experience) + get
# test post(rate + experience) + get + include
# test post(rate + experience) + get + filter
# test post(rate + experience) + get + filter + include
# test patch + get + filter + include
# test put + get + filter + include
# test patch(experience) + get + filter + include
def test_rates():
    url = "http://127.0.0.1:5000{}"
    clean(url)

    # test post(rate) + get
    rate_1 = post("rates", {"currency": "USD"})
    assert len(get("rates")) == 1
    assert get("rates")[0]["id"] == rate_1["id"]

    # test post(rate + experience) + get
    # test post(rate + experience) + get + include
    # test post(rate + experience) + get + filter
    # test post(rate + experience) + get + filter + include
    experience_1 = post("experience", {"status": "Active", "commission": 20})
    assert "commission" in experience_1
    rate_2 = post("rates", {"currency": "EUR", "experience": experience_1["id"]})
    assert len(get("rates?currency=EUR")) == 1
    assert get("rates?currency=EUR")[0]["experience"]["id"] == experience_1["id"]
    assert (
        get("rates?$include=experience&currency=EUR")[0]["experience"]["id"]
        == experience_1["id"]
    )
    assert (
        get("rates?$include=experience&currency=EUR")[0]["experience"]["commission"]
        == experience_1["commission"]
    )

    # test patch + get + filter + include
    rate_1_2 = patch("rates", {"id": rate_1["id"], "currency": "EUR"})
    assert len(get("rates?currency=EUR")) == 2
    assert get("rates?currency=EUR")[1]["experience"]["id"] == experience_1["id"]
    assert (
        get("rates?$include=experience&currency=EUR")[1]["experience"]["id"]
        == experience_1["id"]
    )
    assert (
        get("rates?$include=experience&currency=EUR")[1]["experience"]["commission"]
        == experience_1["commission"]
    )
    assert len(get("rates?experience__commission=20")) == 1

    # test put + get + filter + include
    rate_1_3 = put("rates", {"id": rate_2["id"], "currency": "EUR"})
    assert len(get("rates?currency=EUR")) == 2
    assert len(get("rates?$include=experience")) == 2
    assert (
        next(
            filter(lambda x: "experience" in x, get("rates?$include=experience")), None
        )
        == None
    )

    # test patch(experience) + get + filter + include
    rate_1_4 = patch("rates", {"id": rate_2["id"], "experience": experience_1["id"]})
    assert (
        next(
            filter(lambda x: "experience" in x, get("rates?$include=experience")), None
        )
        != None
    )
    assert (
        next(
            filter(lambda x: "experience" in x, get("rates?$include=experience")), None
        )["experience"]["commission"]
        == experience_1["commission"]
    )


# post normal + get
# patch embed + get
# put embed + get
# post embed + get
# patch embed + get
# put embed + get
def test_embedded():
    url = "http://127.0.0.1:5000{}"
    clean(url)

    # post normal + get
    rate_1 = post("rates", {"currency": "USD"})
    assert len(get("rates")) == 1
    assert get("rates")[0]["id"] == rate_1["id"]
    assert "price" not in get("rates")[0]
    assert get("rates")[0]["currency"] == "USD"

    # patch embed + get
    rate_1_2 = patch("rates", {"id": rate_1["id"], "price": {"amount": 20}})
    assert get("rates")[0]["id"] == rate_1["id"]
    assert "price" in get("rates")[0]
    assert get("rates")[0]["price"]["amount"] == 20
    assert get("rates")[0]["currency"] == "USD"

    # put embed + get
    rate_1_3 = put("rates", {"id": rate_1_2["id"], "price": {"amount": 30}})
    assert get("rates")[0]["id"] == rate_1["id"]
    assert "price" in get("rates")[0]
    assert get("rates")[0]["price"]["amount"] == 30
    assert "currency" not in get("rates")[0]

    # post embed + get
    rate_2 = post("rates", {"currency": "USD", "price": {"amount": 10}})
    assert len(get("rates")) == 2
    assert len(get("rates?price__amount=10")) == 1


# post normal + get
# patch embed + get
def test_embedded_list():
    url = "http://127.0.0.1:5000{}"
    clean(url)

    # post normal + get
    rate_1 = post("rates", {"currency": "USD"})
    assert len(get("rates")) == 1
    assert get("rates")[0]["id"] == rate_1["id"]
    assert "price" not in get("rates")[0]
    assert get("rates")[0]["currency"] == "USD"

    # patch embed + get
    rate_1_2 = patch("rates", {"id": rate_1["id"], "excluded": [{"name": "John"}]})
    assert get("rates")[0]["id"] == rate_1["id"]
    assert len(get("rates")[0]["excluded"]) == 1
    assert get("rates")[0]["excluded"][0]["name"] == "John"
