"""The falcon webapp to use in testing plume.

Serves as an example of making a web app with plume
"""
from datetime import datetime
from marshmallow import Schema, fields
from plume.schema import MongoSchema
from plume import create_app, Collection, Item
import simplejson

class UserSchema(MongoSchema):
    """Example user schema for testing
    """

    class Meta:
        json_module = simplejson
        constraints = (('name', {}), ('email', {'unique': True}))

    name = fields.Str(required=True)
    email = fields.Email(required=True)
    created = fields.DateTime(
        missing=lambda: datetime.utcnow().isoformat(),
        default=lambda: datetime.utcnow().isoformat()
    )
    profile = fields.Nested("ProfileSchema")
    slug = fields.Method("make_slug")

    def make_slug(self, obj):
        return obj['name'].lower().replace(" ", "_")


class ProfileSchema(Schema):
    """Example of nesting a schema.
    In mongodb, this will be a nested document
    """
    class Meta:
        json_module = simplejson

    biography = fields.Str()
    profile_image = fields.Url(load_from='profileImage', dump_to='profileImage')


class FilterSchema(MongoSchema):
    class Meta:
        json_module = simplejson

    value = fields.Str()
    value1 = fields.Str()
    value2 = fields.Str()

    def get_filter(self, req):
        """Only returns
        """
        return {'projection': ('value', 'value1')}


def create():
    """Create the falcon app
    """
    user = UserSchema()
    filters = FilterSchema()
    resources = (
        Collection(user, '/users'), Item(user, '/users/{email}'),
        Collection(filters, '/filters'), Item(filters, '/filters/{value}'),
    )

    return create_app(resources)
