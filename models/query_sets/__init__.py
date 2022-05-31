from mongoengine import QuerySet
import requests
from bson.objectid import ObjectId


class RatesQuerySet(QuerySet):
    def minimum(self, cls, filters):

        pipeline = [
            {"$match": {"experiences": ObjectId(filters.get("experiences"))}},
            {"$unwind": "$rateTypesPrices"},
            {"$sort": {"rateTypesPrices.retailPrice.amount": 1}},
            {"$limit": 1},
        ]

        return list(cls.objects().aggregate(pipeline))


class ExperiencesQuerySet(QuerySet):
    def default(self, cls, filters):
        experiences = cls.fetch(filters)

        for experience in experiences:
            rates = requests.get(
                "http://localhost:5000/api/rates?$queryset=minimum&experiences={}".format(
                    experience["id"]
                )
            )

            rates = rates.json()

            if any(rates):
                experience["minimumRate"] = (
                    rates[0].get("rateTypesPrices", [{}])[0].get("retailPrice", {})
                )

        return experiences


class BookingsQuerySet(QuerySet):
    pass

