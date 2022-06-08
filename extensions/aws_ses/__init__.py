from os import environ

# third party imports
import boto3

# Local application imports
from endpoints import Resource
from flask import request


# Create a new SES resource and specify a region.
client = boto3.client("ses")
default_source = environ.get("AWS_SES_DEFAULT_SOURCE")


def dispatch_request(self, *args, **kwargs):
    pass


Resource.dispatch_requests.append(dispatch_request)
