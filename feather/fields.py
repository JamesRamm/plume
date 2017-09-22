from marshmallow import fields
from bson.objectid import ObjectId


class Slug(fields.Field):
    """Represents a slug. Massages
    the input value to a lowercase string
    without spaces.
    """
    def _serialize(self, value, attr, obj):
        if value:
            return str(value).lower().replace(' ', '-')

class MongoId(fields.Field):
    """Represents a MongoDB object id

    Serializes the ObjectID to a string and
    deserializes to an ObjectID
    """

    def _serialize(self, value, attr, obj):
        return str(value)

    def _deserialize(self, value, attr, obj):
        return ObjectId(value)
