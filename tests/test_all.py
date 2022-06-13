import pytest
import requests
from datetime import datetime
from datetime import timedelta
from datetime import timezone
from dateutil.parser import isoparse


url = "http://127.0.0.1:5000/api/{}"


def delete(table):
    response = requests.get(url.format("{}/fetch".format(table)))
    items = response.json()

    for item in items:
        requests.delete(url.format("{}/{}".format(table, item["id"])))


def clean():
    for item in ["bookings", "rates", "experiences"]:
        delete(item)


def get(endpoint):
    response = requests.get(url.format(endpoint))
    return response.json()


def post(endpoint, data):
    response = requests.post(url.format(endpoint), json=data)
    return response.json()


def post_rate(data={}):
    exp_1 = post("experiences", {"name": "exp_1", "cutOffTime": 24})
    today = datetime(
        datetime.now().year, datetime.now().month, datetime.now().day, 0, 0, 0
    )
    baseRate = {
        "maxParticipants": 10,
        "privateGroup": {
            "minimumGroupRetailPrice": {"amount": 40, "currency": "EUR"},
        },
        "rateTypesPrices": [
            {"rateType": "Adult", "retailPrice": {"amount": 40, "currency": "EUR"}}
        ],
        "dateRange": {
            "from": (today + timedelta(days=3)).isoformat(),
            "until": (today + timedelta(days=6)).isoformat(),
        },
        "startTimes": [
            {"timeSlot": "11:30", "daysOfTheWeek": [0, 1, 2, 3, 4, 5, 6]},
            {
                "timeSlot": "12:30",
                "daysOfTheWeek": [
                    6,
                ],
            },
        ],
    }
    return post("experiences/{}/rates".format(exp_1["id"]), {**baseRate, **data})


def post_experience(data):
    exp = post("experiences", data)
    today = datetime(
        datetime.now().year, datetime.now().month, datetime.now().day, 0, 0, 0
    )

    post(
        "experiences/{}/rates".format(exp["id"]),
        {
            "maxParticipants": 10,
            "privateGroup": {
                "minimumGroupRetailPrice": {"amount": 40, "currency": "EUR"},
            },
            "rateTypesPrices": [
                {"rateType": "Adult", "retailPrice": {"amount": 40, "currency": "EUR"}}
            ],
            "dateRange": {
                "from": (today + timedelta(days=2)).isoformat(),
                "until": (today + timedelta(days=4)).isoformat(),
            },
            "startTimes": [
                {"timeSlot": "11:30", "daysOfTheWeek": [0, 1, 2]},
                {
                    "timeSlot": "12:30",
                    "daysOfTheWeek": [
                        6,
                    ],
                },
            ],
        },
    )

    return exp


def patch(endpoint, data):
    response = requests.patch(url.format(endpoint), json=data)
    return response.json()


def put(endpoint, data):
    response = requests.put(url.format(endpoint), json=data)
    return response.json()


def assert_count(query, count):
    assert len(get(query)) == count


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

    exp_1 = post_experience({"name": "exp_1", "cutOffTime": 10})
    assert_count("experiences", 1)

    exp_2 = post_experience({"name": "exp_2", "cutOffTime": 20})

    assert_count("experiences", 2)
    assert_count("experiences?name=exp_2", 1)
    assert_count("experiences?cutOffTime__gt=15", 1)
    assert_count("experiences?cutOffTime__gt=19", 1)
    assert_count("experiences?cutOffTime__gte=19", 1)
    assert_count("experiences?cutOffTime__gte=20", 1)
    assert_count("experiences?cutOffTime__gt=20", 0)
    assert_count("experiences?cutOffTime__lt=20", 1)
    assert_count("experiences?cutOffTime__lte=20", 2)

    exp_3 = post_experience(
        {
            "name": "exp_3",
            "cutOffTime": 20,
            "partner": {"name": "Jack", "partnerType": "Cars"},
        },
    )
    assert_count("experiences?", 3)
    assert_count("experiences?partner__exists", 1)
    assert_count("experiences?partner__name=Jack", 1)
    assert_count("experiences?partner__name=Jack&partner__partnerType=Cars", 1)
    assert "partner" in return_one("experiences?partner__exists")
    assert "name" in return_one("experiences?partner__exists")["partner"]
    assert "partnerType" in return_one("experiences?partner__exists")["partner"]

    exp_4 = post_experience(
        {
            "name": "exp_4",
            "cutOffTime": 20,
            "partner": {"name": "John", "partnerType": "Boats"},
        },
    )
    assert_count("experiences?", 4)
    assert_count("experiences?$limit=2", 2)
    assert_count("experiences?$skip=1", 3)
    assert_count("experiences?partner__exists", 2)
    assert_count("experiences?$limit=1&partner__exists", 1)
    assert_count("experiences?$skip=1&partner__exists", 1)
    assert_count("experiences?partner__name=Jack", 1)
    assert "partner" in return_one("experiences?partner__name=Jack")
    assert "name" in return_one("experiences?partner__name=Jack")["partner"]
    assert return_one("experiences?partner__name=Jack")["partner"]["name"] == "Jack"
    assert "partnerType" in return_one("experiences?partner__name=Jack")["partner"]

    exp_5 = post_experience(
        {
            "name": "exp_5",
            "cutOffTime": 20,
            "partner": {"name": "John", "partnerType": "Boats"},
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

    assert_count("experiences?", 5)
    assert_count("experiences?images__exists", 5)
    assert_count("experiences?images__ne=[]", 1)
    assert_count("experiences?images__0__urlHigh=High_1", 1)
    assert_count("experiences?images__1__urlHigh=High_2", 1)
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

    exp_1 = post_experience(
        {"name": "exp_1", "rating": {"score": 4.5, "reviewsCount": 1200}}
    )
    exp_2 = post_experience(
        {"name": "exp_2", "rating": {"score": 4.2, "reviewsCount": 100}}
    )
    exp_3 = post_experience(
        {"name": "exp_3", "rating": {"score": 4.8, "reviewsCount": 1000}}
    )
    exp_4 = post_experience(
        {"name": "exp_4", "rating": {"score": 3.8, "reviewsCount": 32}}
    )
    assert_count("experiences", 4)

    assert get("experiences?$sort=rating__score")[0]["id"] == exp_4["id"]
    assert get("experiences?$sort=rating__score")[1]["id"] == exp_2["id"]
    assert get("experiences?$sort=rating__score")[2]["id"] == exp_1["id"]
    assert get("experiences?$sort=rating__score")[3]["id"] == exp_3["id"]

    exp_5 = post_experience(
        {"name": "exp_5", "rating": {"score": 4.2, "reviewsCount": 101}}
    )

    exp_6 = post_experience(
        {"name": "exp_6", "rating": {"score": 4.5, "reviewsCount": 50}}
    )

    exp_7 = post_experience(
        {"name": "exp_7", "rating": {"score": 4.5, "reviewsCount": 5000}}
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

    exp_1 = post_experience({"name": "exp_1"})
    exp_2 = post_experience({"name": "exp_2", "status": "active"})
    assert_count("experiences", 2)

    assert get("experiences/{}".format(exp_1["id"]))["status"] == "draft"
    assert get("experiences/{}".format(exp_2["id"]))["status"] == "active"

    patch("experiences/{}".format(exp_1["id"]), {"status": "active"})
    assert_count("experiences?status=active", 2)


def test_experience_minimum_rate():
    clean()

    exp_1 = post("experiences", {"name": "exp_1"})
    exp_2 = post("experiences", {"name": "exp_2"})
    exp_3 = post("experiences", {"name": "exp_3"})

    # exp_1 will have two rates. 10 will be the lowest
    rate_1_exp_1 = post(
        "rates",
        {
            "experienceId": exp_1["id"],
            "rateTypesPrices": [
                {"retailPrice": {"amount": 50}},
                {"retailPrice": {"amount": 40}},
                {"retailPrice": {"amount": 30}},
            ],
        },
    )
    rate_2_exp_1 = post(
        "rates",
        {
            "experienceId": exp_1["id"],
            "rateTypesPrices": [
                {"retailPrice": {"amount": 100}},
                {"retailPrice": {"amount": 10}},
                {"retailPrice": {"amount": 30}},
            ],
        },
    )

    assert (
        return_one("experiences?id={}".format(exp_1["id"]))["minimumRate"]["amount"]
        == 10
    )

    # exp_2 will have two rates. 20 will be the lowest in two different places
    rate_1_exp_2 = post(
        "rates",
        {
            "experienceId": exp_2["id"],
            "rateTypesPrices": [
                {"retailPrice": {"amount": 50}},
                {"retailPrice": {"amount": 20}},
                {"retailPrice": {"amount": 30}},
            ],
        },
    )
    rate_2_exp_2 = post(
        "rates",
        {
            "experienceId": exp_2["id"],
            "rateTypesPrices": [
                {"retailPrice": {"amount": 100}},
                {"retailPrice": {"amount": 20}},
                {"retailPrice": {"amount": 30}},
            ],
        },
    )

    assert (
        return_one("experiences?id={}".format(exp_2["id"]))["minimumRate"]["amount"]
        == 20
    )

    # exp_3 will have one rate. 0 will be the lowest
    rate_1_exp_3 = post(
        "rates",
        {
            "experienceId": exp_3["id"],
            "rateTypesPrices": [
                {"retailPrice": {"amount": 50}},
                {"retailPrice": {"amount": 20}},
                {"retailPrice": {"amount": 30}},
            ],
        },
    )
    rate_2_exp_3 = post(
        "rates",
        {
            "experienceId": exp_3["id"],
            "rateTypesPrices": [
                {"retailPrice": {"amount": 100}},
                {"retailPrice": {"amount": 20}},
                {"retailPrice": {"amount": 0}},
            ],
        },
    )

    assert (
        return_one("experiences?id={}".format(exp_3["id"]))["minimumRate"]["amount"]
        == 0
    )


def test_experience_minimum_rate():
    clean()

    exp_1 = post_experience({"name": "exp_1"})
    exp_2 = post_experience(
        {"name": "exp_2", "meetingPoint": {"location": [20.0, 0.12]}}
    )
    exp_3 = post_experience(
        {
            "name": "exp_3",
            "meetingPoint": {"location": {"type": "Point", "coordinates": [50, 0.5]}},
        },
    )

    assert_count("experiences", 3)
    assert_count("experiences?meetingPoint__exists", 2)
    assert return_one("experiences?meetingPoint__exists&name=exp_3").get(
        "meetingPoint"
    ).get("location").get("coordinates") == [50, 0.5]
    assert return_one("experiences?meetingPoint__exists&name=exp_2").get(
        "meetingPoint"
    ).get("location").get("coordinates") == [20, 0.12]


def test_experience_id_rates():
    clean()
    today = datetime(
        datetime.now().year, datetime.now().month, datetime.now().day, 0, 0, 0
    )
    baseRate = {
        "privateGroup": {
            "minimumGroupRetailPrice": {"amount": 40, "currency": "EUR"},
        },
        "rateTypesPrices": [
            {"rateType": "Adult", "retailPrice": {"amount": 40, "currency": "EUR"}}
        ],
        "dateRange": {
            "from": (today + timedelta(days=2)).isoformat(),
            "until": (today + timedelta(days=4)).isoformat(),
        },
        "startTimes": [
            {"timeSlot": "11:30", "daysOfTheWeek": [0, 1, 2]},
            {
                "timeSlot": "12:30",
                "daysOfTheWeek": [
                    6,
                ],
            },
        ],
    }

    fromDate = today + timedelta(days=1)
    untilDate = today + timedelta(days=4)

    exp_1 = post("experiences", {"name": "exp_1"})
    exp_2 = post("experiences", {"name": "exp_2"})

    rate_1_exp_1 = post(
        "experiences/{}/rates".format(exp_1["id"]), {**baseRate, "maxParticipants": 10}
    )
    rate_2_exp_1 = post(
        "experiences/{}/rates".format(exp_1["id"]), {**baseRate, "maxParticipants": 20}
    )
    rate_1_exp_2 = post(
        "experiences/{}/rates".format(exp_2["id"]), {**baseRate, "maxParticipants": 5}
    )
    rate_2_exp_2 = post(
        "experiences/{}/rates".format(exp_2["id"]), {**baseRate, "maxParticipants": 2}
    )
    rate_2_exp_3 = post(
        "experiences/{}/rates".format(exp_2["id"]), {**baseRate, "maxParticipants": 6}
    )

    assert_count(
        "experiences/{}/rates?from={}&until={}".format(
            exp_1["id"], fromDate, untilDate
        ),
        2,
    )
    assert_count(
        "experiences/{}/rates?from={}&until={}".format(
            exp_2["id"], fromDate, untilDate
        ),
        3,
    )
    assert_count(
        "experiences/{}/rates?from={}&until={}&maxParticipants=2".format(
            exp_2["id"], fromDate, untilDate
        ),
        1,
    )
    assert_count(
        "experiences/{}/rates?from={}&until={}&maxParticipants__gt=2".format(
            exp_2["id"], fromDate, untilDate
        ),
        2,
    )
    assert_count(
        "experiences/{}/rates?from={}&until={}&maxParticipants__lt=2".format(
            exp_2["id"], fromDate, untilDate
        ),
        0,
    )
    assert_count(
        "experiences/{}/rates?from={}&until={}&maxParticipants__gte=2".format(
            exp_2["id"], fromDate, untilDate
        ),
        3,
    )


def test_booking_trigger():
    clean()

    rate = post_rate()

    booking = post(
        "bookings",
        {
            "rateId": rate["id"],
            "travelerInformation": {
                "firstName": "John",
                "lastName": "Doe",
            },
            "notes": {
                "fromSeller": "This is an imaginary person",
                "fromTraveller": "I am an imaginary person",
            },
            "start": rate["dates"][0]["time"],
            "privateGroup": True,
            "ratesQuantity": [{"rateType": "Adult", "quantity": 2}],
        },
    )

    assert (
        get("rates/{}".format(rate["id"])).get("dates", [])[0]["availableQuantity"] == 8
    )


def test_booking_trigger_private_group_not_enough_slots():
    clean()

    rate = post_rate()
    booking = post(
        "bookings",
        {
            "rateId": rate["id"],
            "travelerInformation": {
                "firstName": "John",
                "lastName": "Doe",
            },
            "notes": {
                "fromSeller": "This is an imaginary person",
                "fromTraveller": "I am an imaginary person",
            },
            "start": rate["dates"][0]["time"],
            "privateGroup": True,
            "ratesQuantity": [{"rateType": "Adult", "quantity": 12}],
        },
    )

    assert "message" in booking
    assert "Not enough slots available for booking" in booking["message"]


def test_booking_trigger_private_group_no_private_groups_allowed():
    clean()

    rate = post_rate({"privateGroup": None})
    booking = post(
        "bookings",
        {
            "rateId": rate["id"],
            "travelerInformation": {
                "firstName": "John",
                "lastName": "Doe",
            },
            "notes": {
                "fromSeller": "This is an imaginary person",
                "fromTraveller": "I am an imaginary person",
            },
            "start": rate["dates"][0]["time"],
            "privateGroup": True,
            "ratesQuantity": [{"rateType": "Adult", "quantity": 2}],
        },
    )

    assert "message" in booking
    assert "This rate does not allow private groups" in booking["message"]


def test_booking_trigger_private_group_already_booked():
    clean()

    rate = post_rate()
    booking = post(
        "bookings",
        {
            "rateId": rate["id"],
            "travelerInformation": {
                "firstName": "John",
                "lastName": "Doe",
            },
            "notes": {
                "fromSeller": "This is an imaginary person",
                "fromTraveller": "I am an imaginary person",
            },
            "start": rate["dates"][0]["time"],
            "privateGroup": True,
            "ratesQuantity": [{"rateType": "Adult", "quantity": 2}],
        },
    )

    assert "id" in booking

    booking = post(
        "bookings",
        {
            "rateId": rate["id"],
            "travelerInformation": {
                "firstName": "John",
                "lastName": "Doe",
            },
            "notes": {
                "fromSeller": "This is an imaginary person",
                "fromTraveller": "I am an imaginary person",
            },
            "start": rate["dates"][0]["time"],
            "privateGroup": True,
            "ratesQuantity": [{"rateType": "Adult", "quantity": 2}],
        },
    )

    assert "Private booking for this timeslot not available" in booking["message"]


def test_booking_trigger_not_enough_slots():
    clean()

    rate = post_rate()

    for x in range(0, 5):
        booking = post(
            "bookings",
            {
                "rateId": rate["id"],
                "travelerInformation": {
                    "firstName": "John",
                    "lastName": "Doe",
                },
                "notes": {
                    "fromSeller": "This is an imaginary person",
                    "fromTraveller": "I am an imaginary person",
                },
                "start": rate["dates"][0]["time"],
                "ratesQuantity": [{"rateType": "Adult", "quantity": 2}],
            },
        )

        assert "id" in booking

    booking = post(
        "bookings",
        {
            "rateId": rate["id"],
            "travelerInformation": {
                "firstName": "John",
                "lastName": "Doe",
            },
            "notes": {
                "fromSeller": "This is an imaginary person",
                "fromTraveller": "I am an imaginary person",
            },
            "start": rate["dates"][0]["time"],
            "ratesQuantity": [{"rateType": "Adult", "quantity": 2}],
        },
    )

    assert "Not enough slots available for booking" in booking["message"]


def test_booking_within_24_hours_of_cutoffTime():
    clean()
    today = datetime(
        datetime.now().year, datetime.now().month, datetime.now().day, 0, 0, 0
    )

    rate = post_rate(
        {
            "dateRange": {
                "from": (today + timedelta(days=1)).isoformat(),
                "until": (today + timedelta(days=6)).isoformat(),
            },
            "startTimes": [
                {"timeSlot": "01:00", "daysOfTheWeek": [0, 1, 2, 3, 4, 5, 6]}
            ],
        }
    )
    booking = post(
        "bookings",
        {
            "rateId": rate["id"],
            "travelerInformation": {
                "firstName": "John",
                "lastName": "Doe",
            },
            "notes": {
                "fromSeller": "This is an imaginary person",
                "fromTraveller": "I am an imaginary person",
            },
            "start": rate["dates"][0]["time"],
            "privateGroup": True,
            "ratesQuantity": [{"rateType": "Adult", "quantity": 2}],
        },
    )

    assert "Cannot book this experience with less than" in booking.get("message")


def test_min_rate_within_timerange():
    clean()

    exp_1 = post("experiences", {"name": "exp_1", "cutOffTime": 24})
    today = datetime(
        datetime.now().year, datetime.now().month, datetime.now().day, 0, 0, 0
    )
    baseRate = {
        "maxParticipants": 10,
        "privateGroup": {
            "minimumGroupRetailPrice": {"amount": 40, "currency": "EUR"},
        },
        "rateTypesPrices": [
            {"rateType": "Adult", "retailPrice": {"amount": 40, "currency": "EUR"}}
        ],
        "dateRange": {
            "from": (today + timedelta(days=5)).isoformat(),
            "until": (today + timedelta(days=7)).isoformat(),
        },
        "startTimes": [
            {"timeSlot": "11:30", "daysOfTheWeek": [0, 1, 2, 3, 4, 5, 6]},
        ],
    }
    post("experiences/{}/rates".format(exp_1["id"]), baseRate)
    post(
        "experiences/{}/rates".format(exp_1["id"]),
        {
            **baseRate,
            "rateTypesPrices": [
                {"rateType": "Adult", "retailPrice": {"amount": 20, "currency": "EUR"}}
            ],
            "dateRange": {
                "from": (today + timedelta(days=5)).isoformat(),
                "until": (today + timedelta(days=7)).isoformat(),
            },
        },
    )
    post(
        "experiences/{}/rates".format(exp_1["id"]),
        {
            **baseRate,
            "rateTypesPrices": [
                {"rateType": "Adult", "retailPrice": {"amount": 10, "currency": "EUR"}}
            ],
            "dateRange": {
                "from": (today + timedelta(days=65)).isoformat(),
                "until": (today + timedelta(days=70)).isoformat(),
            },
        },
    )

    assert return_one("experiences")["minPrice"]["amount"] == 20


def test_email():
    clean()

    rate = post_rate()
    booking = post(
        "bookings",
        {
            "rateId": rate["id"],
            "travelerInformation": {
                "firstName": "John",
                "lastName": "Doe",
                # "email": "isebarn182@gmail.com",
            },
            "notes": {
                "fromSeller": "This is an imaginary person",
                "fromTraveller": "I am an imaginary person",
            },
            "start": rate["dates"][0]["time"],
            "privateGroup": True,
            "ratesQuantity": [{"rateType": "Adult", "quantity": 2}],
        },
    )

    assert "id" in booking


def test_experienceId_rateId_query():
    clean()

    exp_1 = post("experiences", {"name": "exp_1", "cutOffTime": 24})
    today = datetime(
        datetime.now().year, datetime.now().month, datetime.now().day, 0, 0, 0
    )
    baseRate = {
        "maxParticipants": 10,
        "privateGroup": {
            "minimumGroupRetailPrice": {"amount": 40, "currency": "EUR"},
        },
        "rateTypesPrices": [
            {"rateType": "Adult", "retailPrice": {"amount": 40, "currency": "EUR"}}
        ],
        "dateRange": {
            "from": (today + timedelta(days=5)).isoformat(),
            "until": (today + timedelta(days=7)).isoformat(),
        },
        "startTimes": [
            {"timeSlot": "11:30", "daysOfTheWeek": [0, 1, 2, 3, 4, 5, 6]},
        ],
    }
    post("experiences/{}/rates".format(exp_1["id"]), baseRate)
    post(
        "experiences/{}/rates".format(exp_1["id"]),
        {
            **baseRate,
            "rateTypesPrices": [
                {"rateType": "Adult", "retailPrice": {"amount": 20, "currency": "EUR"}}
            ],
            "dateRange": {
                "from": (today + timedelta(days=5)).isoformat(),
                "until": (today + timedelta(days=7)).isoformat(),
            },
        },
    )
    test_rate = post(
        "experiences/{}/rates".format(exp_1["id"]),
        {
            **baseRate,
            "rateTypesPrices": [
                {"rateType": "Adult", "retailPrice": {"amount": 10, "currency": "EUR"}}
            ],
            "dateRange": {
                "from": (today + timedelta(days=65)).isoformat(),
                "until": (today + timedelta(days=70)).isoformat(),
            },
        },
    )

    assert_count("rates", 3)

    assert (
        get("experiences/{}/rates/{}".format(exp_1["id"], test_rate["id"]))[
            "rateTypesPrices"
        ][0]["retailPrice"]["amount"]
        == 10
    )


def test_delete_rate():
    clean()
    rate = post_rate()

    result = requests.delete(
        "http://localhost:5000/api/experiences/{}/rates/{}".format(
            rate["experienceId"], rate["id"]
        )
    )

    assert "Rate {} deleted".format(rate["id"]) in result.json()["message"]


def test_delete_rate_fail():
    clean()

    rate = post_rate()
    booking = post(
        "bookings",
        {
            "rateId": rate["id"],
            "travelerInformation": {
                "firstName": "John",
                "lastName": "Doe",
            },
            "notes": {
                "fromSeller": "This is an imaginary person",
                "fromTraveller": "I am an imaginary person",
            },
            "start": rate["dates"][0]["time"],
            "privateGroup": True,
            "ratesQuantity": [{"rateType": "Adult", "quantity": 2}],
        },
    )

    result = requests.delete(
        "http://localhost:5000/api/experiences/{}/rates/{}".format(
            rate["experienceId"], rate["id"]
        )
    )

    assert result.status_code == 400
    assert "Could not delete document" in result.json()["message"]


def test_put_rate():
    clean()

    rate = post_rate()

    for item in rate["dates"]:
        item["availableQuantity"] -= 1

    rate["maxParticipants"] -= 1

    rate_updated = put(
        "experiences/{}/rates/{}".format(rate["experienceId"], rate["id"]),
        rate,
    )

    rate = post_rate()

    for org, new in zip(rate["dates"], rate_updated["dates"]):
        assert (org["availableQuantity"] - 1) == new["availableQuantity"]

    assert rate["maxParticipants"] - 1 == rate_updated["maxParticipants"]


def test_patch_rate():
    clean()

    rate = post_rate()

    rate["dates"][3]["availableQuantity"] -= 2
    rate_updated = patch(
        "experiences/{}/rates/{}/availability".format(rate["experienceId"], rate["id"]),
        rate["dates"][3],
    )

    rate = post_rate()

    assert (
        rate["dates"][3]["availableQuantity"] - 2
        == rate_updated["dates"][3]["availableQuantity"]
    )


def test_booking_with_incorrect_datetime():
    clean()

    rate = post_rate()

    booking = post(
        "bookings",
        {
            "rateId": rate["id"],
            "travelerInformation": {
                "firstName": "John",
                "lastName": "Doe",
            },
            "notes": {
                "fromSeller": "This is an imaginary person",
                "fromTraveller": "I am an imaginary person",
            },
            "start": (
                isoparse(rate["dates"][-1]["time"]) + timedelta(days=3)
            ).isoformat(),
            "privateGroup": True,
            "ratesQuantity": [{"rateType": "Adult", "quantity": 2}],
        },
    )

    assert booking["message"] == "Not enough slots available for booking"
