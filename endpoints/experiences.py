from endpoints import api
from endpoints import Resource
from models import Rates
from models import Experiences
from flask import request


@api.route("/experiences/<experience_id>/rates")
class ExperiencesController(Resource):
    @api.marshal_list_with(api.models.get("rates"), skip_none=True)
    def get(self, experience_id):
        query = "experienceId__id={}&".format(experience_id)
        query += request.url.split("?")[1] if len(request.url.split("?")) > 1 else ""
        return Rates.objects.query_by_experience(Rates, query)


@api.route("/experiences/fetch")
class ExperienceFetchController(Resource):
    api.model("experiences_fetch", Experiences.model(api))

    def get(self):
        return Experiences.fetch(request.args)
