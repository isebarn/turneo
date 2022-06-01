from endpoints import api
from endpoints import Resource
from models import Rates


@api.route("/experiences/<experience_id>/rates")
class ExperiencesController(Resource):
    @api.marshal_list_with(api.models.get("rates"), skip_none=True)
    def get(self, experience_id):
        return Rates.objects.query_by_experience(Rates, experience_id)
