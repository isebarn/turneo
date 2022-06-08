# Third party imports
from flask import request
from flask_restx import Namespace

# Local application imports
from endpoints import Resource
from extensions.aws_ses.methods import send_email

api = Namespace("aws_ses/email", description="")


@api.route("")
class Email(Resource):
    def post(self):
        send_email(**request.get_json())
