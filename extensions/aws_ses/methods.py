from extensions.aws_ses import client
from extensions.aws_ses import default_source


def send_email(**kwargs):
    client.send_email(
        Destination={"ToAddresses": kwargs.get("receivers")},
        Message={
            "Body": {
                "Html": {
                    "Charset": "UTF-8",
                    "Data": kwargs.get("body"),
                }
            },
            "Subject": {
                "Charset": "UTF-8",
                "Data": kwargs.get("subject"),
            },
        },
        Source=kwargs.get("sender", default_source),
    )
