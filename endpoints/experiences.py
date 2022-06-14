from datetime import datetime
from datetime import timedelta
from datetime import timezone
from requests import get
from requests import post
from requests import patch
from requests import put
from dateutil.parser import isoparse

from flask import abort
from flask import request

from models import Experiences
from models import Images
from models import Rates
from endpoints import api
from endpoints import Resource


@api.route("/experiences/<experience_id>/rates")
class ExperiencesController(Resource):
    @api.marshal_list_with(api.models.get("rates"), skip_none=True)
    def get(self, experience_id):
        if "from" not in request.args or "until" not in request.args:
            abort(400, "from or until missing from query")

        request.args["experienceId__id"] = experience_id
        request.args["dates__time__gte"] = request.args.pop("from")
        request.args["dates__time__lte"] = request.args.pop("until")

        return Rates.fetch(request.args)

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
    @api.marshal_with(api.models.get("rates"), skip_none=True)
    def get(self, experience_id, rate_id):
        query = "experienceId={}&id={}".format(experience_id, rate_id)
        query += request.url.split("?")[1] if len(request.url.split("?")) > 1 else ""
        result = Rates.objects.query_by_experience(Rates, query)
        if result:
            return result[0]
        return {}

    @api.marshal_with(api.models.get("rates"), skip_none=True)
    def patch(self, experience_id, rate_id):
        return patch(
            "http://localhost:5000/api/rates/{}".format(rate_id),
            json={**request.get_json(), "experienceId": experience_id},
        ).json()

    def delete(self, experience_id, rate_id):
        Rates.objects.get(id=rate_id).delete()
        return {"message": "Rate {} deleted".format(rate_id)}


@api.route("/experiences/<experience_id>/rates/<rate_id>/availability")
class ExperienceRateAvailabilityController(Resource):
    @api.marshal_with(api.models.get("rates"), skip_none=True)
    @api.expect(api.models.get("dates"))
    def patch(self, experience_id, rate_id):
        rate = Rates.objects.get(id=rate_id)
        data = request.get_json()

        item = next(
            filter(
                lambda x: x.time == isoparse(data.get("time").replace("Z", "")),
                rate.dates,
            ),
            None,
        )

        if not item:
            abort("Rate with this time does not exist")

        item.availableQuantity = data.get("availableQuantity", item.availableQuantity)
        item.privateGroupStatus = data.get(
            "privateGroupStatus", item.privateGroupStatus
        )

        rate.save()

        return rate.to_json()


@api.route("/experiences/fetch")
class ExperienceFetchController(Resource):
    api.model("experiences_fetch", Experiences.model(api))

    def get(self):
        return Experiences.fetch(request.args)


@api.route("/experiences/<experience_id>/images")
class ExperienceImageController(Resource):
    api.model("experiences_fetch", Experiences.model(api))

    def post(self, experience_id):
        experience = Experiences.objects.get(id=experience_id)
        files = request.files.getlist("file")

        for file in files:
            post(
                "http://localhost:5000/aws_s3/images/image/{}__{}".format(
                    str(experience.id), len(experience.images) + 1
                ),
                files={"file": file},
            )

            image = "https://turneo.s3.amazonaws.com/{}/{}"

            experience.images.append(
                Images(
                    **{
                        "urlHigh": image.format(
                            str(experience.id), len(experience.images) + 1, ""
                        ),
                        "urlLow": image.format(
                            str(experience.id),
                            str(len(experience.images) + 1) + "_thumbnail",
                        ),
                    }
                )
            )

        experience.save()
        return experience.to_json()
