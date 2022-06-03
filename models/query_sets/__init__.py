from mongoengine import QuerySet
import requests
from bson.objectid import ObjectId


class RatesQuerySet(QuerySet):
    def minimum(self, cls, filters):
        return list(
            cls.objects().aggregate(
                [
                    {"$match": {"experienceId": ObjectId(filters.get("experiences"))}},
                    {"$unwind": "$rateTypesPrices"},
                    {"$sort": {"rateTypesPrices.retailPrice.amount": 1}},
                    {"$limit": 1},
                ]
            )
        )

    def query_by_experience(self, cls, query):
        return requests.get("http://localhost:5000/api/rates?{}".format(query)).json()


class ExperiencesQuerySet(QuerySet):
    def default(self, cls, filters):
        experiences = cls.fetch(filters)

        for experience in experiences:
            rates = requests.get(
                "http://localhost:5000/api/rates?$queryset=minimum&experienceId={}".format(
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


class TestQuerySet(QuerySet):
    pass
