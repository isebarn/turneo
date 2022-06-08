from mongoengine import signals
from models import Experiences
from models import Bookings
from models import Rates
from requests import get
from flask import abort
from datetime import datetime
from dateutil.parser import isoparse
from datetime import timezone


def private_group(rate, item, document):

    if not item.privateGroupStatus:
        raise abort(400, "Private booking for this timeslot not available")

    elif not rate.privateGroup:
        raise abort(400, "This rate does not allow private groups")

    else:
        total = 0
        total_price = sum(
            [
                next(
                    filter(
                        lambda prices: prices.rateType == rateQuantity.rateType,
                        rate.rateTypesPrices,
                    )
                ).retailPrice.amount
                * rateQuantity.quantity
                for rateQuantity in document.ratesQuantity
            ]
        )

        if total_price < rate.privateGroup.minimumGroupRetailPrice.amount:
            abort(
                400,
                "Minimum price for private group is {}".format(
                    rate.privateGroup.minimumGroupRetailPrice.amount
                ),
            )


def available_bookings_check(sender, document):
    rate = Rates.objects.get(id=document.rateId.id)
    experience = Experiences.objects.get(id=rate.experienceId.id)

    diff = isoparse(document.start) - datetime.now(timezone.utc)
    hours = diff.days * 24 + diff.seconds / 3600

    if hours < experience.cutOffTime:
        abort(
            400,
            "Cannot book this experience with less than {} hour notice".format(
                experience.cutOffTime
            ),
        )

    item = next(
        filter(
            lambda x: x.time.isoformat() == document.start.replace("Z", ""),
            rate.dates,
        )
    )

    if document.privateGroup:
        private_group(rate, item, document)

    item.availableQuantity -= sum([x.quantity for x in document.ratesQuantity])
    item.privateGroupStatus = False

    if item.availableQuantity < 0:
        raise abort(400, "Not enough slots available for booking")

    rate.save()


def update_booking(sender, document):
    document.bookingLastModified = datetime.now(timezone.utc)


signals.pre_save.connect(available_bookings_check, sender=Bookings)
signals.pre_save.connect(update_booking, sender=Bookings)
