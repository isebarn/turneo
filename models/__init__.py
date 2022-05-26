# Standard library imports
from json import loads
from json import load
from os import _exists
from os import environ
from datetime import datetime

# Third party imports
from bson import json_util
from bson.objectid import ObjectId
from mongoengine import connect
from mongoengine import Document
from mongoengine import ReferenceField
from mongoengine import DictField
from mongoengine import ListField
from mongoengine import MapField
from mongoengine import EmbeddedDocument as _EmbeddedDocument
from mongoengine import EmbeddedDocumentField
from mongoengine import EmbeddedDocumentListField
from mongoengine import DictField
from mongoengine import signals
from mongoengine import NULLIFY
from mongoengine import DateTimeField as _DateTimeField
from mongoengine import FloatField as _FloatField
from mongoengine import IntField as _IntField
from mongoengine import BooleanField as _BooleanField
from mongoengine import StringField as _StringField
from flask_restx.fields import DateTime
from flask_restx.fields import Float
from flask_restx.fields import Integer
from flask_restx.fields import List
from flask_restx.fields import Nested
from flask_restx.fields import String
from flask_restx.fields import Boolean
from flask_restx.fields import Raw


class DateTimeField(_DateTimeField):
    class ISOFormat(DateTime):
        def format(self, value):
            try:
                if isinstance(value, datetime):
                    return value.isoformat()
                return value.get("$date")
            except ValueError as ve:
                raise MarshallingError(ve)

    marshal = ISOFormat


class ImageField(_StringField):
    class AWSImage(String):
        def format(self, value):
            try:
                return get_presigned_url(value)
            except ValueError as ve:
                raise MarshallingError(ve)

    marshal = AWSImage


class FloatField(_FloatField):
    marshal = Float


class IntField(_IntField):
    marshal = Integer


class BooleanField(_BooleanField):
    marshal = Boolean


class StringField(_StringField):
    marshal = String


user = environ.get("username", "root")
password = environ.get("password", "root")
host = environ.get("host", "127.0.0.1")
database_name = environ.get("DB_NAME", "data")

if _exists("rds-combined-ca-bundle.pem"):
    db = connect(
        database_name,
        username=user,
        password=password,
        host=host,
        retryWrites=False,
        ssl_ca_certs="rds-combined-ca-bundle.pem",
    )

else:
    db = connect(
        database_name,
        username=user,
        password=password,
        host=host,
        authentication_source="admin",
    )


class Extended(Document):
    meta = {"abstract": True, "allow_inheritance": True}

    def __init__(self, *args, **kwargs):
        if "id" in kwargs:
            super(Document, self).__init__(*args, **kwargs)

        else:  # Create new document and recursively create or link to existing ReferenceField docs
            super(Document, self).__init__(
                *args,
                **{
                    k: v
                    for k, v in kwargs.items()
                    if not (isinstance(v, dict) or isinstance(v, list))
                }
            )

            for key, value in self._fields.items():
                if isinstance(value, ListField) and key in kwargs:
                    for (i, item) in enumerate(kwargs.get(key, [])):
                        if isinstance(kwargs[key], Document):
                            continue

                        elif isinstance(item, dict) and "id" in item:
                            kwargs[key][i] = value.field.document_type_obj.objects.get(
                                id=item["id"]
                            )

                        elif isinstance(item, str) and ObjectId.is_valid(item):
                            kwargs[key][i] = value.field.document_type_obj.objects.get(
                                id=item
                            )

                        else:
                            kwargs[key][i] = value.field.document_type_obj(**item)

                    setattr(self, key, kwargs[key])

                if isinstance(value, ReferenceField) and key in kwargs:
                    print(123)
                    # link to existing
                    if isinstance(kwargs[key], Document):
                        setattr(self, key, kwargs[key])

                    # pass entire object
                    if "id" in kwargs[key]:
                        setattr(
                            self,
                            key,
                            value.document_type_obj.objects.get(id=kwargs[key]["id"]),
                        )

                    # pass ObjectId string of object
                    elif ObjectId.is_valid(kwargs.get(key, "")):
                        setattr(
                            self,
                            key,
                            value.document_type_obj.objects.get(id=kwargs[key]),
                        )

                    # create new ReferenceField
                    else:
                        setattr(
                            self,
                            key,
                            value.document_type_obj(**{key: {"id": kwargs[key]}}),
                        )

                elif isinstance(value, EmbeddedDocumentField) and key in kwargs:
                    setattr(self, key, value.document_type_obj(**kwargs.get(key)))

                # special for Raw fields that are wildcards
                elif isinstance(value, DictField) and isinstance(kwargs.get(key), dict):
                    setattr(self, key, kwargs.get(key))

            self.save()

    def to_json(self):
        def f(v):
            if isinstance(v, dict) and "$oid" in v:
                return v["$oid"]
            elif isinstance(v, list):
                return list(map(lambda x: f(x), v))
            else:
                return v

        data = {**{k: f(v) for k, v in loads(json_util.dumps(self.to_mongo())).items()}}
        data.update({"id": data.pop("_id")})

        return data

    @classmethod
    def set(cls, *args, **kwargs):
        id = kwargs.pop("id")
        item = cls.objects.get(id=id)

        # ???
        for key, value in kwargs.items():

            if isinstance(value, list) and any(value):
                string_object_ids = [
                    x.get("id") if isinstance(x, dict) else x for x in value
                ]
                if all(map(lambda x: ObjectId.is_valid(x), string_object_ids)):
                    kwargs[key] = [ObjectId(x) for x in string_object_ids]

            elif isinstance(value, dict) and "id" in value:
                kwargs[key] = value["id"]

        cls.objects(id=id).update_one(
            **{
                key.replace("$", "")
                if key.startswith("$")
                else "set__{}".format(key): (
                    ObjectId(value) if ObjectId.is_valid(value) else value
                )
                for key, value in kwargs.items()
            }
        )

        return cls.objects.get(id=id)

    @classmethod
    def update(cls, *args, **kwargs):
        id = kwargs.pop("id")
        item = cls.objects.get(id=id)

        # ???
        for key, value in kwargs.items():
            if isinstance(value, list) and any(value):
                string_object_ids = [x.get("id", {}).get("$oid") for x in value]
                if all(map(lambda x: ObjectId.is_valid(x), string_object_ids)):
                    value = [ObjectId(x) for x in string_object_ids]

            elif isinstance(value, dict) and "id" in value:
                kwargs[key] = value["id"]

        [delattr(item, k) for k, v in cls._fields.items() if k not in ["_cls", "id"]]

        item.save()

        cls.objects(id=id).update_one(
            **{
                key.replace("$", "")
                if key.startswith("$")
                else "set__{}".format(key): (
                    ObjectId(value) if ObjectId.is_valid(value) else value
                )
                for key, value in kwargs.items()
            }
        )
        return cls.objects.get(id=id)

    @classmethod
    def get(cls, *args, **kwargs):
        def recursively_query(model, fields, search, root=False):

            if fields == "id__in":
                return {fields: search}

            if "__" not in fields:
                if root:
                    return {fields: search}

                return [x.id for x in model.objects(**{fields: search})]

            prop, fields = fields.split("__", 1)

            result = recursively_query(
                model._fields[prop].field.document_type_obj
                if isinstance(model._fields[prop], ListField)
                else model._fields[prop].document_type_obj,
                fields,
                search,
            )

            if not root:
                return [x.id for x in model.objects(**{"{}__in".format(prop): result})]
            else:
                return {"{}__in".format(prop): result}

        filters = {}
        for query, search in kwargs.items():
            if query.startswith("$"):
                continue

            if query.split("__")[0] in cls._fields.keys():
                filters.update({query: search})

            else:
                filters.update(
                    {
                        key: list(set(value) & set(filters.get(key, value)))
                        if isinstance(value, list)
                        else value
                        for key, value in recursively_query(
                            cls, query, search, True
                        ).items()
                    }
                )

        return (
            cls.objects(**filters)
            .skip(int(kwargs.get("$skip", 0)))
            .limit(int(kwargs.get("$limit", 0)))
        )

    @classmethod
    def post_save(cls, sender, document, **kwargs):
        if kwargs.get("created"):
            pass

    @classmethod
    def pre_save(cls, sender, document, **kwargs):
        if (
            document.to_json().get("_id")
            and next(cls.objects(id=document.id)).status is not document.status
        ):
            pass

    @classmethod
    def base(cls):
        return {
            **{
                key: getattr(cls, key).marshal
                for key, value in list(cls._fields.items())
                if hasattr(getattr(cls, key), "marshal")
            },
            "id": String(),
        }

    @classmethod
    def reference(cls):
        return {
            **cls.base(),
            **{
                field: String()
                for field, instance in cls._fields.items()
                if isinstance(instance, ReferenceField)
            },
        }

    @classmethod
    def model(cls, api):
        return {
            **cls.base(),
            **{
                field: Nested(api.models.get(field), skip_none=True)
                for field, instance in cls._fields.items()
                if isinstance(instance, ReferenceField)
                or isinstance(instance, DictField)
                or isinstance(instance, EmbeddedDocumentField)
            },
            **{
                field: List(
                    Nested(
                        api.models.get(field),
                        skip_none=True,
                    ),
                )
                for field, instance in cls._fields.items()
                if isinstance(instance, ListField)
            },
        }

    @classmethod
    def _reference_fields(cls):
        return {
            key: value
            for key, value in cls._fields.items()
            if isinstance(value, ReferenceField)
        }

    @classmethod
    def _list_reference_fields(cls):
        return {
            key: value
            for key, value in cls._fields.items()
            if isinstance(value, ListField)
            and isinstance(cls._fields[key].field, ReferenceField)
        }

    @classmethod
    def fetch(cls, filters):
        include = filters.pop("$include", "").split(",")
        data = [x.to_json() for x in list(cls.get(**filters))]

        for key, value in cls._list_reference_fields().items():
            if key in include:
                id_lists = list(map(lambda x: x[key], data))
                ids = list(set([item for sublist in id_lists for item in sublist]))

                values = value.field.document_type_obj.fetch(
                    {
                        "$include": ",".join(
                            [
                                x.replace("{}__".format(key), "")
                                for x in include
                                if x.startswith(key)
                            ]
                        ),
                        "id__in": ids,
                    },
                )

                values = {x["id"]: x for x in values}

                for item in data:
                    item.update({key: [values[x] for x in item[key]]})

            else:
                for item in data:
                    item.update({key: [{"id": x} for x in item[key]]})

        for key, value in cls._reference_fields().items():
            if key in include:
                ids = [x.get(key) for x in data if key in x]
                values = value.document_type_obj.fetch(
                    {
                        "$include": ",".join(
                            [
                                x.replace("{}__".format(key), "")
                                for x in include
                                if x.startswith(key)
                            ]
                        ),
                        "id__in": ids,
                    },
                )

                values = {x["id"]: x for x in values}

                for item in data:
                    if key in item and item[key] in values:
                        item[key] = values[item[key]]

            else:
                list(
                    map(
                        lambda x: x.update(
                            {key: ({"id": x.get(key)} if key in x else None)}
                        ),
                        data,
                    )
                )

        return data


class EmbeddedDocument(_EmbeddedDocument):
    meta = {"abstract": True, "allow_inheritance": True}

    @classmethod
    def base(cls):
        return {
            **{
                key: getattr(cls, key).marshal
                for key, value in list(cls._fields.items())
                if hasattr(getattr(cls, key), "marshal")
            }
        }

    @classmethod
    def reference(cls):
        return {
            **cls.base(),
        }

    @classmethod
    def model(cls, api):
        return {
            **cls.base(),
        }


class Organizer(EmbeddedDocument):
    name = StringField()
    type = StringField()
    partnerId = StringField()


class Meetingpoint(EmbeddedDocument):
    address = StringField()
    city = StringField()
    country = StringField()
    gmapsLink = StringField()


class Pickup(EmbeddedDocument):
    value = BooleanField(default=False)
    rules = StringField()


class Duration(EmbeddedDocument):
    days = IntField()
    hours = IntField()
    minutes = IntField()


class Externallinks(EmbeddedDocument):
    name = StringField()
    url = StringField()


class Images(EmbeddedDocument):
    urlHigh = StringField()
    urlLow = StringField()
    altText = StringField()


class Rating(EmbeddedDocument):
    score = FloatField()
    reviewsCount = IntField()


class Included(EmbeddedDocument):
    name = StringField()
    inclusion_id = StringField()


class Excluded(EmbeddedDocument):
    name = StringField()
    exclusion_id = StringField()


class Experience(Extended):
    status = StringField()
    name = StringField()
    code = StringField()
    category = StringField()
    highlight = StringField()
    description = StringField()
    cancellationPolicy = StringField()
    video = StringField()
    otherNotes = StringField()
    organizer = EmbeddedDocumentField(Organizer)
    meetingPoint = EmbeddedDocumentField(Meetingpoint)
    pickup = EmbeddedDocumentField(Pickup)
    duration = EmbeddedDocumentField(Duration)
    externalLinks = EmbeddedDocumentField(Externallinks)
    rating = EmbeddedDocumentField(Rating)
    images = EmbeddedDocumentListField(Images)
    included = EmbeddedDocumentListField(Included)
    excluded = EmbeddedDocumentListField(Excluded)


class Dates(EmbeddedDocument):
    date = DateTimeField()
    availableQuantity = IntField()
    private_group = BooleanField(default=False)


class Price(EmbeddedDocument):
    price = StringField()
    amount = IntField()
    currency = StringField()


class PrivateGroup(EmbeddedDocument):
    amount = IntField()
    currency = StringField()


class Rates(Extended):
    status = StringField()
    dates = EmbeddedDocumentListField(Dates)
    experience = ReferenceField(Experience, reverse_delete_rule=NULLIFY)
    maxParticipants = IntField()
    prices = EmbeddedDocumentListField(Price)
    private_group = EmbeddedDocumentField(PrivateGroup)



# def config():
    # signals.pre_save.connect(Class.pre_save, sender=Class)
    # signals.post_save.connect(Class.post_save, sender=Class)

    # seed
    # logging.info("Seeding database")
    # seed = load(open("models/seed.json"))

    # helper method to remove "_id" and "_cls" so I can compare json objects
    # from the db
    # def remove_meta_from_dict_item(item):
    #     item.pop("_cls")
    #     item.pop("_id")
    #     for key, value in item.items():
    #         if isinstance(value, dict):
    #             remove_meta_from_dict_item(value)


# config()