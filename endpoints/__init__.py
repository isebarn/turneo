# Standard library imports
import os
from datetime import datetime
from requests import post
from requests import get

# Third party imports
from flask import Flask
from flask import request
from flask import g
from flask_restx import Namespace
from flask_restx import Resource as _Resource
from flask_restx.fields import DateTime
from flask_restx.fields import Float
from flask_restx.fields import Integer
from flask_restx.fields import List
from flask_restx.fields import Nested
from flask_restx.fields import String
from flask_restx.fields import Boolean
from flask_restx.fields import Raw

# Local application imports
import models


api = Namespace("api", description="")
organizer_base = api.model("organizer_base", models.Organizer.base())
organizer_reference = api.model("organizer_reference", models.Organizer.reference())
organizer_full = api.model("organizer", models.Organizer.model(api))
meetingpoint_base = api.model("meetingpoint_base", models.Meetingpoint.base())
meetingpoint_reference = api.model(
    "meetingpoint_reference", models.Meetingpoint.reference()
)
meetingpoint_full = api.model("meetingpoint", models.Meetingpoint.model(api))
pickup_base = api.model("pickup_base", models.Pickup.base())
pickup_reference = api.model("pickup_reference", models.Pickup.reference())
pickup_full = api.model("pickup", models.Pickup.model(api))
duration_base = api.model("duration_base", models.Duration.base())
duration_reference = api.model("duration_reference", models.Duration.reference())
duration_full = api.model("duration", models.Duration.model(api))
externallinks_base = api.model("externallinks_base", models.Externallinks.base())
externallinks_reference = api.model(
    "externallinks_reference", models.Externallinks.reference()
)
externallinks_full = api.model("externallinks", models.Externallinks.model(api))
images_base = api.model("images_base", models.Images.base())
images_reference = api.model("images_reference", models.Images.reference())
images_full = api.model("images", models.Images.model(api))
rating_base = api.model("rating_base", models.Rating.base())
rating_reference = api.model("rating_reference", models.Rating.reference())
rating_full = api.model("rating", models.Rating.model(api))
included_base = api.model("included_base", models.Included.base())
included_reference = api.model("included_reference", models.Included.reference())
included_full = api.model("included", models.Included.model(api))
excluded_base = api.model("excluded_base", models.Excluded.base())
excluded_reference = api.model("excluded_reference", models.Excluded.reference())
excluded_full = api.model("excluded", models.Excluded.model(api))
experience_base = api.model("experience_base", models.Experience.base())
experience_reference = api.model("experience_reference", models.Experience.reference())
experience_full = api.model("experience", models.Experience.model(api))
dates_base = api.model("dates_base", models.Dates.base())
dates_reference = api.model("dates_reference", models.Dates.reference())
dates_full = api.model("dates", models.Dates.model(api))
price_base = api.model("price_base", models.Price.base())
price_reference = api.model("price_reference", models.Price.reference())
price_full = api.model("price", models.Price.model(api))
private_group_base = api.model("private_group_base", models.PrivateGroup.base())
private_group_reference = api.model(
    "private_group_reference", models.PrivateGroup.reference()
)
private_group_full = api.model("private_group", models.PrivateGroup.model(api))
rates_base = api.model("rates_base", models.Rates.base())
rates_reference = api.model("rates_reference", models.Rates.reference())
rates_full = api.model("rates", models.Rates.model(api))


class Resource(_Resource):
    dispatch_requests = []

    def __init__(self, api=None, *args, **kwargs):
        super(Resource, self).__init__(api, args, kwargs)

    def dispatch_request(self, *args, **kwargs):

        tmp = request.args.to_dict()
        request.args = tmp

        if request.method == "POST":
            json = request.get_json()

            for key, value in json.items():
                if isinstance(value, dict) and key in routes:
                    if "id" in value:
                        json[key] = value["id"]

                    else:
                        item = post(
                            "http://localhost:5000/api/{}".format(key), json=value
                        )
                        json[key] = item.json()["id"]

        for method in self.dispatch_requests:
            method(self, args, kwargs)

        return super(Resource, self).dispatch_request(*args, **kwargs)


@api.route("/experience")
class ExperienceController(Resource):

    # @api.marshal_list_with(api.models.get('experience'), skip_none=True)
    def get(self):
        return models.Experience.fetch(request.args)

    # @api.marshal_with(api.models.get('experience'), skip_none=True)
    def post(self):
        return models.Experience.post(request.get_json())

    # @api.marshal_with(api.models.get('experience'), skip_none=True)
    def put(self):
        return models.Experience.put(request.get_json())

    # @api.marshal_with(api.models.get('experience'), skip_none=True)
    def patch(self):
        return models.Experience.patch(request.get_json())


@api.route("/experience/<experience_id>")
class BaseExperienceController(Resource):
    # @api.marshal_with(api.models.get("experience"), skip_none=True)
    def get(self, experience_id):
        return models.Experience.objects.get(id=experience_id)

    def delete(self, experience_id):
        return models.Experience.get(id=experience_id).delete()


@api.route("/experience/base")
class BaseExperienceController(Resource):

    # @api.marshal_list_with(api.models.get('experience_reference'))
    def get(self):
        return [x.to_json() for x in models.Experience.get(**request.args)]


@api.route("/rates")
class RatesController(Resource):

    # @api.marshal_list_with(api.models.get('rates'), skip_none=True)
    def get(self):
        return models.Rates.fetch(request.args)

    # @api.marshal_with(api.models.get('rates'), skip_none=True)
    def post(self):
        return models.Rates.post(request.get_json())

    # @api.marshal_with(api.models.get('rates'), skip_none=True)
    def put(self):
        return models.Rates.put(request.get_json())

    # @api.marshal_with(api.models.get('rates'), skip_none=True)
    def patch(self):
        return models.Rates.patch(request.get_json())


@api.route("/rates/<rates_id>")
class BaseRatesController(Resource):
    # @api.marshal_with(api.models.get("rates"), skip_none=True)
    def get(self, rates_id):
        return models.Rates.objects.get(id=rates_id)

    def delete(self, rates_id):
        return models.Rates.get(id=rates_id).delete()


@api.route("/rates/base")
class BaseRatesController(Resource):

    # @api.marshal_list_with(api.models.get('rates_reference'))
    def get(self):
        return [x.to_json() for x in models.Rates.get(**request.args)]


routes = list(set([x.urls[0].split("/")[1] for x in api.resources]))
