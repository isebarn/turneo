from mongoengine import QuerySet
import requests
from bson.objectid import ObjectId
from datetime import datetime
from datetime import timedelta
from dateutil.parser import isoparse
from datetime import timezone
from utils.querystring import querystring

# This file contains querysets
# What are querysets
# When querying the models, you do
# ModelName.objects({
#   field_1: value_1
#   .
#   .
#   field_n: value_2
# })
# A queryset is shorthand for this. You define a method called fx custom_query_1
# And now you can execute ModelName.objects.custom_query_1
# The api supports directly calling a queryset by calling
# GET /api/ModelName?$queryset=custom_query_1


def get(query):
    result = requests.get("http://localhost:5000/api/{}".format(query))
    return result.json()


class RatesQuerySet(QuerySet):
    def default(self, cls, filters):
        rates = cls.fetch(filters)

        return rates

    def minimum(self, cls, filters):
        result = next(
            cls.objects().aggregate(
                [
                    {
                        "$match": {
                            "experienceId": ObjectId(filters.get("experienceId")),
                            "availableDates": {
                                "$elemMatch": {
                                    "time": {
                                        "$lte": datetime.now() + timedelta(days=60)
                                    }
                                }
                            },
                        }
                    },
                    {"$unwind": "$rateTypesPrices"},
                    {"$sort": {"rateTypesPrices.retailPrice.amount": 1}},
                    {"$limit": 1},
                ]
            ),
            None,
        )

        return result

    def query_by_experience(self, cls, query):
        return requests.get("http://localhost:5000/api/rates?{}".format(query)).json()

    def fetch(self, cls, filters):
        return cls.fetch(filters)


class ExperiencesQuerySet(QuerySet):
    def default(self, cls, filters):
        # These can be passed to include rates
        fromDate = filters.pop("from", None)
        untilDate = filters.pop("until", None)
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

            if minimumRate:
                experience["minPrice"] = minimumRate.get("rateTypesPrices", [{}])[
                    0
                ].get("retailPrice", {})

            query_string = {"$queryset": "fetch", "experienceId": experience["id"]}

            if fromDate and untilDate:
                query_string.update(
                    {
                        "availableDates__time__gte": fromDate,
                        "availableDates__time__lte": untilDate,
                    }
                )

            rates = requests.get(
                querystring("http://localhost:5000/api/rates", query_string)
            )
            experience.update({"rateCalendar": rates.json()})

        if fromDate and untilDate:
            experiences = list(
                filter(lambda x: any(x.get("rateCalendar", [])), experiences)
            )

        if skip:
            experiences = experiences[int(skip) :]

        if limit:
            experiences = experiences[: int(limit)]

        return experiences

    def fetch(self, cls, filters):
        return cls.fetch(filters)


class BookingsQuerySet(QuerySet):
    def default(self, cls, filters):
        bookings = cls.fetch(filters)

        rates = cls.rateId.document_type_obj.fetch(
            {"id__in": list(set([x["rateId"] for x in bookings]))}
        )

        experiences = cls.rateId.document_type_obj.experienceId.document_type_obj.fetch(
            {"id__in": list(set([x["experienceId"] for x in rates]))}
        )

        for booking in bookings:
            rate = next(filter(lambda x: x["id"] == booking["rateId"], rates))
            experience = next(
                filter(lambda x: x["id"] == rate["experienceId"], experiences)
            )
            date = next(
                filter(lambda x: x["dateId"] == booking["availabilityId"], rate["availableDates"]), None
            )

            booking["ratesBooked"] = {
                "rateId": booking["rateId"],
                "start": isoparse(date.get("time", {}).get("$date")),
                "ratesQuantity": booking["ratesQuantity"],
            }

            booking["experience"] = experience

            booking["price"] = {
                "finalRetailPrice": {"amount": 0, "currency": "EUR"},
                "retailPriceBreakdown": [],
            }

            for item in booking["ratesQuantity"]:
                price = next(
                    filter(
                        lambda x: item["rateType"] == x["rateType"],
                        rate["rateTypesPrices"],
                    )
                )
                booking["price"]["retailPriceBreakdown"].append(
                    {**price, "quantity": item["quantity"]}
                )
                booking["price"]["finalRetailPrice"]["amount"] += (
                    price.get("retailPrice", {}).get("amount")
                ) * item["quantity"]

            booking["cancellationFee"] = {
                "amount": booking["price"]["finalRetailPrice"]["amount"]
                if (booking["ratesBooked"]["start"] - datetime.now(timezone.utc)).days
                else 0,
                "currency": booking["price"]["finalRetailPrice"]["currency"],
            }

            booking["bookingCreated"] = ObjectId(booking["id"]).generation_time
            booking['start'] = booking['ratesBooked']['start']

        return bookings
