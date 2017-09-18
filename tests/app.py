"""The falcon webapp to use in testing feather.

Serves as an example of making a web app with feather
"""
from datetime import datetime
from marshmallow import Schema, fields
from feather.schema import MongoSchema
from feather import create_app, Collection, Item

class UserSchema(MongoSchema):
    """Example user schema for testing
    """
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
    biography = fields.Str()
    profile_image = fields.Url(load_from='profileImage', dump_to='profileImage')


def create():
    """Create the falcon app
    """
    user = UserSchema()
    resources = (Collection('/users', user), Item('/users/{email}', user))
    return create_app(resources)
