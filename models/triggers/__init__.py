from mongoengine import signals
from models import Bookings
from requests import get
from flask import abort
from datetime import datetime
from datetime import timezone


def get_rate_and_bookings(document):
    rate = get("http://localhost:5000/api/rates/{}".format(str(document.rateId.id)))
    bookings = get(
        "http://localhost:5000/api/bookings/fetch?rateId={}&start={}".format(
            str(document.rateId.id), document.start
        )
    )

    return rate.json(), bookings.json()


def private_group(document):
    rate, bookings = get_rate_and_bookings(document)
    total_slots = rate.get("maxParticipants", 0)
    total_bookings = sum(
        [x.get("quantity", 0) for y in bookings for x in y.get("ratesQuantity", [])]
    )

    if total_bookings != 0:
        raise abort(400, "Private booking for this time not available")

    elif sum([x.quantity for x in document.ratesQuantity]) > total_slots:
        raise abort(400, "This time does not have enough slots")

    elif not rate.get("privateGroup"):
        raise abort(400, "This time does not allow private groups")

    else:
        total = 0
        total_price = sum(
            [
                next(
                    filter(
                        lambda prices: prices.get("rateType") == rateQuantity.rateType,
                        rate.get("rateTypesPrices", {}),
                    )
                )
                .get("retailPrice", {})
                .get("amount", 0)
                * rateQuantity.quantity
                for rateQuantity in document.ratesQuantity
            ]
        )

        minimum_private_group_price = (
            rate.get("privateGroup", {})
            .get("minimumGroupRetailPrice", {})
            .get("amount", 0)
        )

        if total_price < minimum_private_group_price:
            abort(
                400,
                "Minimum price for private group is {}".format(
                    minimum_private_group_price
                ),
            )


def available_bookings_check(sender, document):
    if document.privateGroup:
        private_group(document)

    else:
        rate, bookings = get_rate_and_bookings(document)
        total_slots = rate.get("maxParticipants", 0)
        total_bookings = sum(
            [x.get("quantity", 0) for y in bookings for x in y.get("ratesQuantity", [])]
        )

        if (total_slots - total_bookings) < sum(
            [x.quantity for x in document.ratesQuantity]
        ):
            raise abort(400, "Not enough slots available for booking")


def update_booking(sender, document):
    document.bookingLastModified = datetime.now(timezone.utc)


signals.pre_save.connect(available_bookings_check, sender=Bookings)
signals.pre_save.connect(update_booking, sender=Bookings)
