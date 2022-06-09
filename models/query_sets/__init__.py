from mongoengine import QuerySet
import requests
from bson.objectid import ObjectId
from datetime import datetime
from datetime import timedelta
from dateutil.parser import isoparse
from datetime import timezone


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
                            "dates": {
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

            if minimumRate:
                experience["minPrice"] = minimumRate.get("rateTypesPrices", [{}])[
                    0
                ].get("retailPrice", {})

            if fromDate and untilDate:
                rates = requests.get(
                    "http://localhost:5000/api/rates?$queryset=fetch&experienceId={}&dateRange__fromDate__gte={}&dateRange__fromDate__lte={}".format(
                        experience["id"], fromDate, untilDate
                    )
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
            {"id__in": list(set([x["rateId"]["id"] for x in bookings]))}
        )

        experiences = cls.rateId.document_type_obj.experienceId.document_type_obj.fetch(
            {"id__in": list(set([x["experienceId"]["id"] for x in rates]))}
        )

        for booking in bookings:
            rate = next(filter(lambda x: x["id"] == booking["rateId"]["id"], rates))
            experience = next(
                filter(lambda x: x["id"] == rate["experienceId"]["id"], experiences)
            )

            booking["ratesBooked"] = {
                "rateId": booking["rateId"]["id"],
                "start": booking["start"],
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
                if (
                    isoparse(booking["start"]["$date"]) - datetime.now(timezone.utc)
                ).days
                else 0,
                "currency": booking["price"]["finalRetailPrice"]["currency"],
            }

            booking["bookingCreated"] = ObjectId(booking["id"]).generation_time

        return bookings
