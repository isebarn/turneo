from datetime import datetime
from datetime import timedelta
from dateutil.parser import isoparse
from datetime import timezone
from endpoints import api
from endpoints import Resource
from models import Rates
from models import Experiences
from flask import request
from requests import post


@api.route("/experiences/<experience_id>/rates")
class ExperiencesController(Resource):
    @api.marshal_list_with(api.models.get("rates"), skip_none=True)
    def get(self, experience_id):
        query = "experienceId__id={}&".format(experience_id)
        query += request.url.split("?")[1] if len(request.url.split("?")) > 1 else ""
        return Rates.objects.query_by_experience(Rates, query)

    def post(self, experience_id):
        rate = request.get_json()
        rate["dates"] = []

        fromDate = isoparse(rate["dateRange"]["from"])
        untilDate = isoparse(rate["dateRange"]["until"])

        for idx in range((untilDate - fromDate).days + 1):
            for startTime in rate["startTimes"]:
                if (fromDate + timedelta(days=idx)).weekday() in startTime[
                    "daysOfTheWeek"
                ]:
                    rate["dates"].append(
                        {
                            "time": (
                                fromDate
                                + timedelta(
                                    days=idx,
                                    hours=int(startTime["timeSlot"].split(":")[0]),
                                    minutes=int(startTime["timeSlot"].split(":")[1]),
                                )
                            ).isoformat(),
                            "availableQuantity": rate["maxParticipants"],
                            "privateGroupStatus": "privateGroup" in rate,
                        }
                    )

        rate.pop("startTimes")
        rate.pop("dateRange")
        rate["experienceId"] = str(experience_id)
        response = post("http://localhost:5000/api/rates", json=rate)
        return response.json()


@api.route("/experiences/<experience_id>/rates/<rate_id>")
class ExperienceRateController(Resource):
    @api.marshal_list_with(api.models.get("rates"), skip_none=True)
    def get(self, experience_id, rate_id):
        query = "experienceId={}&id={}".format(experience_id, rate_id)
        query += request.url.split("?")[1] if len(request.url.split("?")) > 1 else ""
        result = Rates.objects.query_by_experience(Rates, query)
        if result:
            return result[0]
        return {}


@api.route("/experiences/fetch")
class ExperienceFetchController(Resource):
    api.model("experiences_fetch", Experiences.model(api))

    def get(self):
        return Experiences.fetch(request.args)
