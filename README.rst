=======
feather
=======


.. image:: https://img.shields.io/pypi/v/feather.svg
        :target: https://pypi.python.org/pypi/feather

.. image:: https://img.shields.io/travis/JamesRamm/feather.svg
        :target: https://travis-ci.org/JamesRamm/feather

.. image:: https://readthedocs.org/projects/feather/badge/?version=latest
        :target: https://feather.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status

.. image:: https://landscape.io/github/JamesRamm/feather/master/landscape.svg?style=flat
   :target: https://landscape.io/github/JamesRamm/feather/master
   :alt: Code Health

.. image:: https://pyup.io/repos/github/JamesRamm/feather/shield.svg
     :target: https://pyup.io/repos/github/JamesRamm/feather/
     :alt: Updates


Easy webapps with falcon & mongodb

Features
---------------

- Simple interface to MongoDB using ``marshmallow`` schemas. This allows a single document
  definition which also provides serialization and validation

- Standard ``Resource`` classes for creating a full CRUD JSON API for REST collections and items.

- ``FileCollection`` and ``FileItem`` resources provide file upload functionality. They can be configured
    to use feathers' basic ``FileStore`` or your own storage backend (e.g. GridFS)

- Useful extra fields for marshmallow (``Choice``, ``Slug``, ``MongoId``, ``Password``...)


Example
--------

The following example creates a basic JSON API for a representation of a user.

.. code-block:: python

    from datetime import datetime
    from feather import create_app, schema, Collection, Item
    from feather.connection import connect
    from feather.fields import Slug, Choice
    from marshmallow import fields, Schema

    class UserSchema(schema.MongoSchema):
        name = fields.Str(required=True)
        email = fields.Email(required=True)
        created = fields.DateTime(
                missing=lambda: datetime.utcnow().isoformat(),
                default=lambda: datetime.utcnow().isoformat()
        )
        profile = fields.Nested("ProfileSchema")
        slug = fields.Slug(populate_from='name')

    class ProfileSchema(Schema):
        """Example of nesting a schema.
        In mongodb, this will be a nested document
        """
        biography = fields.Str()
        profile_image = fields.Url(load_from='profileImage', dump_to='profileImage')


    def get_app(database_name='myapp')
        """Creates the falcon app.
        We pass the database name so we can use a different db for testing
        """
        # Connect to the database *before* making schema instance.
        # The ``connect`` function takes the same arguments as pymongo's
        # ``MongoClient``. Here we connect to localhost.
        connect(database_name)
        user = UserSchema()
        resources = (Collection(user, '/users'), Item(user, '/users/{email}'))
        return create_app(resources)

Name this file ``app.py`` and run it with gunicorn:

        gunicorn 'app:get_app()'

Philosophy
----------

Feather intends to be a light and transparent library. It should compliment and enhance
Falcon & MongoDB usage but not get in the way of custom development.
To this end I have a small number of rules:

- No 'magic'. That means no overriding operators, writing endless metaclasses or hiding away aspects of Falcon.
  If a user wants to break out and do something different, they shouldn't have to spend ages grokking feather code
  in order to figure out where they can reach into Falcon (or marshmallow or pymongo for that matter).

- Avoid mixins. Mixins introduce implicit dependencies and make it harder to reason about code. There are frameworks out
  there which use mixins liberally (both for falcon and not for falcon). I decided to go a different way.

- No 'batteries' included. Feather is a *library* not a framework. We strive to provide useful functions and classes for common use
  cases, not *all* use cases. It should be possible to use them or not. If you use something, you should not be obliged to have 100 other
  things. (e.g., creating a schema based on ``MongoSchema`` does not oblige you to use feathers' ``Collection`` and/or ``Item`` resource classes).



