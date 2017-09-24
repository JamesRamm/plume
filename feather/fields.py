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

class Choice(fields.Field):
    def __init__(self, choices=None, *args, **kwargs):
        self._choices = choices
        super(Choice, self).__init__(*args, **kwargs)

    def _serialize(self, value, attr, obj):
        if value not in self._choices:
            raise ValidationError('Value must be one of {}'.format(self._choices))
        return {
            'value': value,
            'choices': self._choices
        }

    def _deserialize(self, value, attr, obj):
        if value not in self._choices:
            raise ValidationError('Value must be one of {}'.format(self._choices))
        return value
