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


class Resource(_Resource):
    dispatch_requests = []

    def __init__(self, api=None, *args, **kwargs):
        super(Resource, self).__init__(api, args, kwargs)

    def dispatch_request(self, *args, **kwargs):

        tmp = request.args.to_dict()

        if request.method == "GET":
            request.args = tmp

            [
                tmp.update({k: v.split(",")})
                for k, v in tmp.items()
                if k.endswith("__in")
            ]

            [
                tmp.update({k: v.split(",")})
                for k, v in tmp.items()
                if k.startswith("$sort")
            ]            

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



api = Namespace("api", description="")
organizer_base = api.model('organizer_base', models.Organizer.base())
organizer_reference = api.model('organizer_reference', models.Organizer.reference())
organizer_full = api.model('organizer', models.Organizer.model(api))
meetingPoint_base = api.model('meetingPoint_base', models.MeetingPoint.base())
meetingPoint_reference = api.model('meetingPoint_reference', models.MeetingPoint.reference())
meetingPoint_full = api.model('meetingPoint', models.MeetingPoint.model(api))
pickup_base = api.model('pickup_base', models.Pickup.base())
pickup_reference = api.model('pickup_reference', models.Pickup.reference())
pickup_full = api.model('pickup', models.Pickup.model(api))
duration_base = api.model('duration_base', models.Duration.base())
duration_reference = api.model('duration_reference', models.Duration.reference())
duration_full = api.model('duration', models.Duration.model(api))
externalLinks_base = api.model('externalLinks_base', models.ExternalLinks.base())
externalLinks_reference = api.model('externalLinks_reference', models.ExternalLinks.reference())
externalLinks_full = api.model('externalLinks', models.ExternalLinks.model(api))
rating_base = api.model('rating_base', models.Rating.base())
rating_reference = api.model('rating_reference', models.Rating.reference())
rating_full = api.model('rating', models.Rating.model(api))
images_base = api.model('images_base', models.Images.base())
images_reference = api.model('images_reference', models.Images.reference())
images_full = api.model('images', models.Images.model(api))
included_base = api.model('included_base', models.Included.base())
included_reference = api.model('included_reference', models.Included.reference())
included_full = api.model('included', models.Included.model(api))
excluded_base = api.model('excluded_base', models.Excluded.base())
excluded_reference = api.model('excluded_reference', models.Excluded.reference())
excluded_full = api.model('excluded', models.Excluded.model(api))
experiences_base = api.model('experiences_base', models.Experiences.base())
experiences_reference = api.model('experiences_reference', models.Experiences.reference())
experiences_full = api.model('experiences', models.Experiences.model(api))
minimumGroupRetailPrice_base = api.model('minimumGroupRetailPrice_base', models.MinimumGroupRetailPrice.base())
minimumGroupRetailPrice_reference = api.model('minimumGroupRetailPrice_reference', models.MinimumGroupRetailPrice.reference())
minimumGroupRetailPrice_full = api.model('minimumGroupRetailPrice', models.MinimumGroupRetailPrice.model(api))
privateGroup_base = api.model('privateGroup_base', models.PrivateGroup.base())
privateGroup_reference = api.model('privateGroup_reference', models.PrivateGroup.reference())
privateGroup_full = api.model('privateGroup', models.PrivateGroup.model(api))
dateRange_base = api.model('dateRange_base', models.DateRange.base())
dateRange_reference = api.model('dateRange_reference', models.DateRange.reference())
dateRange_full = api.model('dateRange', models.DateRange.model(api))
retailPrice_base = api.model('retailPrice_base', models.RetailPrice.base())
retailPrice_reference = api.model('retailPrice_reference', models.RetailPrice.reference())
retailPrice_full = api.model('retailPrice', models.RetailPrice.model(api))
rateTypesPrices_base = api.model('rateTypesPrices_base', models.RateTypesPrices.base())
rateTypesPrices_reference = api.model('rateTypesPrices_reference', models.RateTypesPrices.reference())
rateTypesPrices_full = api.model('rateTypesPrices', models.RateTypesPrices.model(api))
startTimes_base = api.model('startTimes_base', models.StartTimes.base())
startTimes_reference = api.model('startTimes_reference', models.StartTimes.reference())
startTimes_full = api.model('startTimes', models.StartTimes.model(api))
rates_base = api.model('rates_base', models.Rates.base())
rates_reference = api.model('rates_reference', models.Rates.reference())
rates_full = api.model('rates', models.Rates.model(api))
travelerInformation_base = api.model('travelerInformation_base', models.TravelerInformation.base())
travelerInformation_reference = api.model('travelerInformation_reference', models.TravelerInformation.reference())
travelerInformation_full = api.model('travelerInformation', models.TravelerInformation.model(api))
notes_base = api.model('notes_base', models.Notes.base())
notes_reference = api.model('notes_reference', models.Notes.reference())
notes_full = api.model('notes', models.Notes.model(api))
ratesQuantity_base = api.model('ratesQuantity_base', models.RatesQuantity.base())
ratesQuantity_reference = api.model('ratesQuantity_reference', models.RatesQuantity.reference())
ratesQuantity_full = api.model('ratesQuantity', models.RatesQuantity.model(api))
bookings_base = api.model('bookings_base', models.Bookings.base())
bookings_reference = api.model('bookings_reference', models.Bookings.reference())
bookings_full = api.model('bookings', models.Bookings.model(api))
experiences_full = api.clone("experiences", experiences_full, {"minimumRate": Nested(retailPrice_full)})

@api.route("/experiences")
class ExperiencesController(Resource):
    @api.marshal_list_with(api.models.get("experiences"), skip_none=True)
    def get(self):
        return models.Experiences.qry(request.args)

    @api.marshal_with(api.models.get("experiences"), skip_none=True)
    def post(self):
        return models.Experiences.post(request.get_json())

    @api.marshal_with(api.models.get("experiences"), skip_none=True)
    def put(self):
        return models.Experiences.put(request.get_json())

    @api.marshal_with(api.models.get("experiences"), skip_none=True)
    def patch(self):
        return models.Experiences.patch(request.get_json())


@api.route("/experiences/<experiences_id>")
class BaseExperiencesController(Resource):
    @api.marshal_with(api.models.get("experiences"), skip_none=True)
    def get(self, experiences_id):
        return models.Experiences.objects.get(id=experiences_id).to_json()

    @api.marshal_with(api.models.get("experiences"), skip_none=True)
    def put(self, experiences_id):
        return models.Experiences.put({"id": experiences_id, **request.get_json()})

    @api.marshal_with(api.models.get("experiences"), skip_none=True)
    def patch(self, experiences_id):
        return models.Experiences.patch({"id": experiences_id, **request.get_json()})

    def delete(self, experiences_id):
        return models.Experiences.get(id=experiences_id).delete()


@api.route("/rates")
class RatesController(Resource):
    @api.marshal_list_with(api.models.get("rates"), skip_none=True)
    def get(self):
        return models.Rates.qry(request.args)

    @api.marshal_with(api.models.get("rates"), skip_none=True)
    def post(self):
        return models.Rates.post(request.get_json())

    @api.marshal_with(api.models.get("rates"), skip_none=True)
    def put(self):
        return models.Rates.put(request.get_json())

    @api.marshal_with(api.models.get("rates"), skip_none=True)
    def patch(self):
        return models.Rates.patch(request.get_json())


@api.route("/rates/<rates_id>")
class BaseRatesController(Resource):
    @api.marshal_with(api.models.get("rates"), skip_none=True)
    def get(self, rates_id):
        return models.Rates.objects.get(id=rates_id).to_json()

    @api.marshal_with(api.models.get("rates"), skip_none=True)
    def put(self, rates_id):
        return models.Rates.put({"id": rates_id, **request.get_json()})

    @api.marshal_with(api.models.get("rates"), skip_none=True)
    def patch(self, rates_id):
        return models.Rates.patch({"id": rates_id, **request.get_json()})

    def delete(self, rates_id):
        return models.Rates.get(id=rates_id).delete()


@api.route("/bookings")
class BookingsController(Resource):
    @api.marshal_list_with(api.models.get("bookings"), skip_none=True)
    def get(self):
        return models.Bookings.qry(request.args)

    @api.marshal_with(api.models.get("bookings"), skip_none=True)
    def post(self):
        return models.Bookings.post(request.get_json())

    @api.marshal_with(api.models.get("bookings"), skip_none=True)
    def put(self):
        return models.Bookings.put(request.get_json())

    @api.marshal_with(api.models.get("bookings"), skip_none=True)
    def patch(self):
        return models.Bookings.patch(request.get_json())


@api.route("/bookings/<bookings_id>")
class BaseBookingsController(Resource):
    @api.marshal_with(api.models.get("bookings"), skip_none=True)
    def get(self, bookings_id):
        return models.Bookings.objects.get(id=bookings_id).to_json()

    @api.marshal_with(api.models.get("bookings"), skip_none=True)
    def put(self, bookings_id):
        return models.Bookings.put({"id": bookings_id, **request.get_json()})

    @api.marshal_with(api.models.get("bookings"), skip_none=True)
    def patch(self, bookings_id):
        return models.Bookings.patch({"id": bookings_id, **request.get_json()})

    def delete(self, bookings_id):
        return models.Bookings.get(id=bookings_id).delete()




routes = list(set([x.urls[0].split('/')[1] for x in api.resources]))