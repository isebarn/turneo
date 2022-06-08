from endpoints import api
from endpoints import Resource
from models import Bookings
from flask import request


@api.route("/bookings/fetch")
class ExperienceFetchController(Resource):
    api.model("bookings_fetch", Bookings.model(api))

    def get(self):
        return Bookings.fetch(request.args)
