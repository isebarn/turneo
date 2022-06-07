from mongoengine import QuerySet
import requests
from bson.objectid import ObjectId
from datetime import datetime
from datetime import timedelta
from dateutil.parser import isoparse


def get(query):
    result = requests.get("http://localhost:5000/api/{}".format(query))
    return result.json()


class RatesQuerySet(QuerySet):
    def default(self, cls, filters):
        rates = cls.fetch(filters)

        bookings = []
        for rate in rates:
            rate["dates"] = []
            fromDate = isoparse(rate["dateRange"]["fromDate"]["$date"])
            untilDate = isoparse(rate["dateRange"]["untilDate"]["$date"])
            for date in range((untilDate - fromDate).days + 1):
                for startTime in rate["startTimes"]:
                    rate["dates"].append(
                        {
                            "time": fromDate
                            + timedelta(
                                days=date,
                                hours=int(startTime["timeSlot"].split(":")[0]),
                                minutes=int(startTime["timeSlot"].split(":")[1]),
                            ),
                            "availableQuantity": rate["maxParticipants"],
                            "privateGroupStatus": "privateGroup" in rate,
                        }
                    )

            bookings = get("bookings?rateId={}".format(rate["id"]))

            for booking in bookings:
                item = next(
                    filter(
                        lambda x: x["time"] == isoparse(booking["start"]),
                        rate["dates"],
                    )
                )

                item["availableQuantity"] -= sum(
                    map(lambda x: x["quantity"], booking["ratesQuantity"])
                )

                item["privateGroupStatus"] = False

        return rates

    def minimum(self, cls, filters):
        return list(
            cls.objects().aggregate(
                [
                    {"$match": {"experienceId": ObjectId(filters.get("experienceId"))}},
                    {"$unwind": "$rateTypesPrices"},
                    {"$sort": {"rateTypesPrices.retailPrice.amount": 1}},
                    {"$limit": 1},
                ]
            )
        )

    def query_by_experience(self, cls, query):
        return requests.get("http://localhost:5000/api/rates?{}".format(query)).json()

    def fetch(self, cls, filters):
        return cls.fetch(filters)


class ExperiencesQuerySet(QuerySet):
    def default(self, cls, filters):
        # These can be passed to include rates
        fromDate = filters.pop("fromDate", None)
        untilDate = filters.pop("untilDate", None)
        limit = filters.pop("$limit", None)
        skip = filters.pop("$skip", None)

        experiences = cls.fetch(filters)

        for experience in experiences:
            minimumRate = requests.get(
                "http://localhost:5000/api/rates?$queryset=minimum&experienceId={}&dateRange__fromDate__lte={}".format(
                    experience["id"], (datetime.now() + timedelta(days=60)).isoformat()
                )
            )

            minimumRate = minimumRate.json()

            if any(minimumRate):
                experience["minPrice"] = (
                    minimumRate[0]
                    .get("rateTypesPrices", [{}])[0]
                    .get("retailPrice", {})
                )

            if fromDate and untilDate:
                rates = requests.get(
                    "http://localhost:5000/api/rates?$queryset=fetch&experienceId={}&dateRange__fromDate__gte={}&dateRange__fromDate__lte={}".format(
                        experience["id"], fromDate, untilDate
                    )
                )
                experience.update({"rateCalendar": rates.json()})

        experiences = list(filter(lambda x: "minPrice" in x, experiences))
        if fromDate and untilDate:
            experiences = list(
                filter(lambda x: any(x.get("rateCalendar", [])), experiences)
            )

        if skip:
            experiences = experiences[int(skip) :]

        if limit:
            experiences = experiences[: int(limit)]

        return experiences


class BookingsQuerySet(QuerySet):
    pass


class TestQuerySet(QuerySet):
    pass
