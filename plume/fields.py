from marshmallow import fields, ValidationError
from bson.objectid import ObjectId


class Slug(fields.Field):
    """Represents a slug. Massages
    the input value to a lowercase string
    without spaces.
    """
    def __init__(self, populate_from=None, *args, **kwargs):
        self._from = populate_from
        super(Slug, self).__init__(*args, **kwargs)

    def _serialize(self, value, attr, obj):
        if value:
            pass
        elif self._from:
            value = obj[self._from]
        else:
            value = ''

        return str(value).lower().replace(' ', '-')

    def _deserialize(self, value, attr, data):
        if value:
            pass
        elif self._from:
            value = data[self._from]

        return str(value).lower().replace(' ', '-')

class MongoId(fields.Field):
    """Represents a MongoDB object id

    Serializes the ObjectID to a string and
    deserializes to an ObjectID
    """

    def _serialize(self, value, *args):
        return str(value)

    def _deserialize(self, value, *args):
        return ObjectId(value)

class Choice(fields.Field):
    """The input value is validated against a set of choices
    passed in the field definition.
    Upon serialization, the full choice list along with the
    chosen value is returned (in a dict).
    Only the chosen value should be passed in deserialization.
    """
    def __init__(self, choices=None, *args, **kwargs):
        self._choices = choices
        super(Choice, self).__init__(*args, **kwargs)

    def _serialize(self, value, *args):
        if value not in self._choices:
            raise ValidationError('Value must be one of {}'.format(self._choices))
        return {
            'value': value,
            'choices': list(self._choices)
        }

    def _deserialize(self, value, *args):
        if value not in self._choices:
            raise ValidationError('Value must be one of {}'.format(self._choices))
        return value
