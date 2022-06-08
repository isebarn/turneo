from endpoints import api
from endpoints import Resource
from models import Rates
from flask import request


@api.route("/rates/fetch")
class ExperienceFetchController(Resource):
    api.model("rates_fetch", Rates.model(api))

    def get(self):
        return Rates.fetch(request.args)
