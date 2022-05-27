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

api = Namespace("api", description="")
organizer_base = api.model('organizer_base', models.Organizer.base())
organizer_reference = api.model('organizer_reference', models.Organizer.reference())
organizer_full = api.model('organizer', models.Organizer.model(api))
meetingpoint_base = api.model('meetingpoint_base', models.Meetingpoint.base())
meetingpoint_reference = api.model('meetingpoint_reference', models.Meetingpoint.reference())
meetingpoint_full = api.model('meetingpoint', models.Meetingpoint.model(api))
pickup_base = api.model('pickup_base', models.Pickup.base())
pickup_reference = api.model('pickup_reference', models.Pickup.reference())
pickup_full = api.model('pickup', models.Pickup.model(api))
duration_base = api.model('duration_base', models.Duration.base())
duration_reference = api.model('duration_reference', models.Duration.reference())
duration_full = api.model('duration', models.Duration.model(api))
externallinks_base = api.model('externallinks_base', models.Externallinks.base())
externallinks_reference = api.model('externallinks_reference', models.Externallinks.reference())
externallinks_full = api.model('externallinks', models.Externallinks.model(api))
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
experience_base = api.model('experience_base', models.Experience.base())
experience_reference = api.model('experience_reference', models.Experience.reference())
experience_full = api.model('experience', models.Experience.model(api))
minimumgroupretailprice_base = api.model('minimumgroupretailprice_base', models.Minimumgroupretailprice.base())
minimumgroupretailprice_reference = api.model('minimumgroupretailprice_reference', models.Minimumgroupretailprice.reference())
minimumgroupretailprice_full = api.model('minimumgroupretailprice', models.Minimumgroupretailprice.model(api))
privategroup_base = api.model('privategroup_base', models.Privategroup.base())
privategroup_reference = api.model('privategroup_reference', models.Privategroup.reference())
privategroup_full = api.model('privategroup', models.Privategroup.model(api))
daterange_base = api.model('daterange_base', models.Daterange.base())
daterange_reference = api.model('daterange_reference', models.Daterange.reference())
daterange_full = api.model('daterange', models.Daterange.model(api))
retailprice_base = api.model('retailprice_base', models.Retailprice.base())
retailprice_reference = api.model('retailprice_reference', models.Retailprice.reference())
retailprice_full = api.model('retailprice', models.Retailprice.model(api))
ratetypesprices_base = api.model('ratetypesprices_base', models.Ratetypesprices.base())
ratetypesprices_reference = api.model('ratetypesprices_reference', models.Ratetypesprices.reference())
ratetypesprices_full = api.model('ratetypesprices', models.Ratetypesprices.model(api))
starttimes_base = api.model('starttimes_base', models.Starttimes.base())
starttimes_reference = api.model('starttimes_reference', models.Starttimes.reference())
starttimes_full = api.model('starttimes', models.Starttimes.model(api))
rates_base = api.model('rates_base', models.Rates.base())
rates_reference = api.model('rates_reference', models.Rates.reference())
rates_full = api.model('rates', models.Rates.model(api))
travelerinformation_base = api.model('travelerinformation_base', models.Travelerinformation.base())
travelerinformation_reference = api.model('travelerinformation_reference', models.Travelerinformation.reference())
travelerinformation_full = api.model('travelerinformation', models.Travelerinformation.model(api))
notes_base = api.model('notes_base', models.Notes.base())
notes_reference = api.model('notes_reference', models.Notes.reference())
notes_full = api.model('notes', models.Notes.model(api))
ratesquantity_base = api.model('ratesquantity_base', models.Ratesquantity.base())
ratesquantity_reference = api.model('ratesquantity_reference', models.Ratesquantity.reference())
ratesquantity_full = api.model('ratesquantity', models.Ratesquantity.model(api))
booking_base = api.model('booking_base', models.Booking.base())
booking_reference = api.model('booking_reference', models.Booking.reference())
booking_full = api.model('booking', models.Booking.model(api))


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

@api.route("/booking")
class BookingController(Resource):

    # @api.marshal_list_with(api.models.get('booking'), skip_none=True)
    def get(self):
        return models.Booking.fetch(request.args)

    # @api.marshal_with(api.models.get('booking'), skip_none=True)
    def post(self):
        return models.Booking.post(request.get_json())

    # @api.marshal_with(api.models.get('booking'), skip_none=True)
    def put(self):
        return models.Booking.put(request.get_json())

    # @api.marshal_with(api.models.get('booking'), skip_none=True)
    def patch(self):
        return models.Booking.patch(request.get_json())


@api.route("/booking/<booking_id>")
class BaseBookingController(Resource):
    # @api.marshal_with(api.models.get("booking"), skip_none=True)
    def get(self, booking_id):
        return models.Booking.objects.get(id=booking_id)

    def delete(self, booking_id):
        return models.Booking.get(id=booking_id).delete()



routes = list(set([x.urls[0].split('/')[1] for x in api.resources]))