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

    rates_1 = post(
        "rates",
        {
            "maxParticipants": 5,
            "dateRange": {"start": "2022-01-01", "until": "2022-01-03"},
        },
    )

    assert len(get("rates")) == 1
    assert len(get("rates?dateRange__start__gte=2022-01-01")) == 1

    rates_2 = post(
        "rates",
        {
            "maxParticipants": 5,
            "dateRange": {"start": "2022-01-02", "until": "2022-01-03"},
        },
    )

    assert len(get("rates")) == 2
    assert len(get("rates?dateRange__start__gte=2022-01-02")) == 1

    rates_3 = post(
        "rates",
        {
            "maxParticipants": 6,
            "dateRange": {"start": "2022-01-03", "until": "2022-01-05"},
        },
    )

    assert len(get("rates")) == 3
    assert len(get("rates?dateRange__start__gte=2022-01-02")) == 2
    assert (
        len(
            get(
                "rates?dateRange__start__gte=2022-01-02&dateRange__start__lte=2022-01-03"
            )
        )
        == 2
    )
    assert (
        len(
            get(
                "rates?\
                dateRange__start__gte=2022-01-02&\
                dateRange__start__lte=\2022-01-03&\
                dateRange__until__gte=2022-01-04"
            )
        )
        == 1
    )

    patch("rates/{}".format(rates_3["id"]), {"dateRange": {"until": "2022-01-10"}})
    assert (
        len(
            get(
                "rates?\
                dateRange__until__gte=2022-01-010"
            )
        )
        == 1
    )


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


# post normal + get
# patch embed + get
# put embed + get
# post embed + get
# patch embed + get
# put embed + get
def test_embedded():
    url = "http://127.0.0.1:5000{}"
    clean(url)

    pass


# post normal + get
# patch embed + get
def test_embedded_list():
    url = "http://127.0.0.1:5000{}"
    clean(url)

    pass
