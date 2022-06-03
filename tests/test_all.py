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


def test_experience_minimum_rate():
    clean()

    exp_1 = post("experiences", {"name": "exp_1"})
    exp_2 = post("experiences", {"name": "exp_2"})
    exp_3 = post("experiences", {"name": "exp_3"})

    # exp_1 will have two rates. 10 will be the lowest
    rate_1_exp_1 = post(
        "rates",
        {
            "experiences": exp_1["id"],
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
            "experiences": exp_1["id"],
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
            "experiences": exp_2["id"],
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
            "experiences": exp_2["id"],
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
            "experiences": exp_3["id"],
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
            "experiences": exp_3["id"],
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

    exp_1 = post("experiences", {"name": "exp_1"})
    exp_2 = post(
        "experiences", {"name": "exp_2", "meetingPoint": {"location": [20.0, 0.12]}}
    )
    exp_3 = post(
        "experiences",
        {
            "name": "exp_3",
            "meetingPoint": {"location": {"type": "Point", "coordinates": [50, 0.5]}},
        },
    )

    assert_count("experiences", 3)
    assert assert_count("experiences?meetingPoint__exists", 2)
    assert return_one("experiences?meetingPoint__exists&name=exp_3").get(
        "meetingPoint"
    ).get("location").get("coordinates") == [50, 0.5]
    assert return_one("experiences?meetingPoint__exists&name=exp_2").get(
        "meetingPoint"
    ).get("location").get("coordinates") == [20, 0.12]


def test_experience_id_rates():
    clean()

    exp_1 = post("experiences", {"name": "exp_1"})
    exp_2 = post("experiences", {"name": "exp_2"})

    rate_1_exp_1 = post("rates", {"experiences": exp_1["id"], "maxParticipants": 10})
    rate_2_exp_1 = post("rates", {"experiences": exp_1["id"], "maxParticipants": 20})
    rate_1_exp_2 = post("rates", {"experiences": exp_2["id"], "maxParticipants": 5})
    rate_2_exp_2 = post("rates", {"experiences": exp_2["id"], "maxParticipants": 2})
    rate_2_exp_3 = post("rates", {"experiences": exp_2["id"], "maxParticipants": 6})

    assert assert_count("experiences/{}/rates".format(exp_1["id"]), 2)
    assert assert_count("experiences/{}/rates".format(exp_2["id"]), 3)
    assert assert_count("experiences/{}/rates?maxParticipants=2".format(exp_2["id"]), 1)
    assert assert_count(
        "experiences/{}/rates?maxParticipants__gt=2".format(exp_2["id"]), 2
    )
    assert assert_count(
        "experiences/{}/rates?maxParticipants__lt=2".format(exp_2["id"]), 0
    )
    assert assert_count(
        "experiences/{}/rates?maxParticipants__gte=2".format(exp_2["id"]), 3
    )


def test_booking_trigger_private_group_minimum_price():
    clean()

    rates = post(
        "rates",
        {
            "maxParticipants": 10,
            "rateTypesPrices": [
                {"rateType": "Adult", "retailPrice": {"amount": 40, "currency": "EUR"}}
            ],
            "privateGroup": {
                "minimumGroupRetailPrice": {"amount": 120, "currency": "EUR"}
            },
            "dateRange": {"fromDate": "2022-05-15", "untilDate": "2022-11-15"},
            "startTimes": [{"timeSlot": "11:30", "daysOfTheWeek": ["Monday"]}],
        },
    )

    booking = post(
        "bookings",
        {
            "rates": rates["id"],
            "travelerInformation": {
                "firstName": "John",
                "lastName": "Doe",
                "email": "john.doe@gmail.com",
            },
            "notes": {
                "fromSeller": "This is an imaginary person",
                "fromTraveller": "I am an imaginary person",
            },
            "start": "2022-03-14T11:00:00Z",
            "privateGroup": True,
            "ratesQuantity": [{"rateType": "Adult", "quantity": 2}],
        },
    )

    assert "message" in booking
    assert "Minimum price" in booking["message"]


def test_booking_trigger_private_group_not_enough_slots():
    clean()

    rates = post(
        "rates",
        {
            "maxParticipants": 10,
            "rateTypesPrices": [
                {"rateType": "Adult", "retailPrice": {"amount": 40, "currency": "EUR"}}
            ],
            "privateGroup": {
                "minimumGroupRetailPrice": {"amount": 120, "currency": "EUR"}
            },
            "dateRange": {"fromDate": "2022-05-15", "untilDate": "2022-11-15"},
            "startTimes": [{"timeSlot": "11:30", "daysOfTheWeek": ["Monday"]}],
        },
    )
    booking = post(
        "bookings",
        {
            "rates": rates["id"],
            "travelerInformation": {
                "firstName": "John",
                "lastName": "Doe",
                "email": "john.doe@gmail.com",
            },
            "notes": {
                "fromSeller": "This is an imaginary person",
                "fromTraveller": "I am an imaginary person",
            },
            "start": "2022-03-14T11:00:00Z",
            "privateGroup": True,
            "ratesQuantity": [{"rateType": "Adult", "quantity": 12}],
        },
    )

    assert "message" in booking
    assert "This time does not have enough slots" in booking["message"]


def test_booking_trigger_private_group_no_private_groups_allowed():
    clean()

    rates = post(
        "rates",
        {
            "maxParticipants": 10,
            "rateTypesPrices": [
                {"rateType": "Adult", "retailPrice": {"amount": 40, "currency": "EUR"}}
            ],
            "dateRange": {"fromDate": "2022-05-15", "untilDate": "2022-11-15"},
            "startTimes": [{"timeSlot": "11:30", "daysOfTheWeek": ["Monday"]}],
        },
    )
    booking = post(
        "bookings",
        {
            "rates": rates["id"],
            "travelerInformation": {
                "firstName": "John",
                "lastName": "Doe",
                "email": "john.doe@gmail.com",
            },
            "notes": {
                "fromSeller": "This is an imaginary person",
                "fromTraveller": "I am an imaginary person",
            },
            "start": "2022-03-14T11:00:00Z",
            "privateGroup": True,
            "ratesQuantity": [{"rateType": "Adult", "quantity": 4}],
        },
    )

    assert "message" in booking
    assert "This time does not allow private groups" in booking["message"]


def test_booking_trigger_private_group_already_booked():
    clean()

    rates = post(
        "rates",
        {
            "maxParticipants": 10,
            "rateTypesPrices": [
                {"rateType": "Adult", "retailPrice": {"amount": 40, "currency": "EUR"}}
            ],
            "privateGroup": {
                "minimumGroupRetailPrice": {"amount": 120, "currency": "EUR"}
            },
            "dateRange": {"fromDate": "2022-05-15", "untilDate": "2022-11-15"},
            "startTimes": [{"timeSlot": "11:30", "daysOfTheWeek": ["Monday"]}],
        },
    )
    successfull_booking = post(
        "bookings",
        {
            "rates": rates["id"],
            "travelerInformation": {
                "firstName": "John",
                "lastName": "Doe",
                "email": "john.doe@gmail.com",
            },
            "notes": {
                "fromSeller": "This is an imaginary person",
                "fromTraveller": "I am an imaginary person",
            },
            "start": "2022-03-14T11:00:00Z",
            "ratesQuantity": [{"rateType": "Adult", "quantity": 1}],
        },
    )

    assert "id" in successfull_booking

    private_booking = post(
        "bookings",
        {
            "rates": rates["id"],
            "travelerInformation": {
                "firstName": "John",
                "lastName": "Doe",
                "email": "john.doe@gmail.com",
            },
            "notes": {
                "fromSeller": "This is an imaginary person",
                "fromTraveller": "I am an imaginary person",
            },
            "start": "2022-03-14T11:00:00Z",
            "privateGroup": True,
            "ratesQuantity": [{"rateType": "Adult", "quantity": 4}],
        },
    )

    assert "Private booking for this time not available" in private_booking["message"]


def test_booking_trigger_not_enough_slots():
    clean()

    rates = post(
        "rates",
        {
            "maxParticipants": 10,
            "rateTypesPrices": [
                {"rateType": "Adult", "retailPrice": {"amount": 40, "currency": "EUR"}}
            ],
            "privateGroup": {
                "minimumGroupRetailPrice": {"amount": 120, "currency": "EUR"}
            },
            "dateRange": {"fromDate": "2022-05-15", "untilDate": "2022-11-15"},
            "startTimes": [{"timeSlot": "11:30", "daysOfTheWeek": ["Monday"]}],
        },
    )

    for x in range(0, 5):
        successfull_booking = post(
            "bookings",
            {
                "rates": rates["id"],
                "travelerInformation": {
                    "firstName": "John",
                    "lastName": "Doe",
                    "email": "john.doe@gmail.com",
                },
                "notes": {
                    "fromSeller": "This is an imaginary person",
                    "fromTraveller": "I am an imaginary person",
                },
                "start": "2022-03-14T11:00:00Z",
                "ratesQuantity": [{"rateType": "Adult", "quantity": 2}],
            },
        )

        assert "id" in successfull_booking

    failed_booking = post(
        "bookings",
        {
            "rates": rates["id"],
            "travelerInformation": {
                "firstName": "John",
                "lastName": "Doe",
                "email": "john.doe@gmail.com",
            },
            "notes": {
                "fromSeller": "This is an imaginary person",
                "fromTraveller": "I am an imaginary person",
            },
            "start": "2022-03-14T11:00:00Z",
            "ratesQuantity": [{"rateType": "Adult", "quantity": 2}],
        },
    )

    assert "Not enough slots available for booking" in failed_booking["message"]
