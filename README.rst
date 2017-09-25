=======
Feather
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


A library to help you make Falcon web apps backed by MongoDB.

Features
---------------

- Simple interface to MongoDB using ``marshmallow`` schemas. This allows a single document
  definition which also provides serialization and validation

- Standard ``Resource`` classes for creating a full CRUD JSON API for REST collections and items.

- Easy filtering/projection of documents per request

- The ``FileCollection`` and ``FileItem`` resources provide file upload functionality. They can be configured
  to use feathers' basic ``FileStore`` or your own storage backend (e.g. GridFS)

- Useful extra fields for marshmallow (``Choice``, ``Slug``, ``MongoId``, ``Password``...)


Example
--------

The following example creates a basic JSON API for a representation of a user.

..  code-block:: python

    from datetime import datetime
    from feather import create_app, schema, Collection, Item
    from feather.connection import connect
    from feather.fields import Slug
    from marshmallow import fields, Schema

    class UserSchema(schema.MongoSchema):
        name = fields.Str(required=True)
        email = fields.Email(required=True)
        created = fields.DateTime(
                missing=lambda: datetime.utcnow().isoformat(),
                default=lambda: datetime.utcnow().isoformat()
        )
        profile = fields.Nested("ProfileSchema")
        slug = Slug(populate_from='name')

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

Design
----------

Feather intends to be a light and transparent library. It should compliment and enhance
Falcon & MongoDB usage but not get in the way of custom development.
To this end I have a small number of rules:

- No magic. Like falcon itself, it should be easy to follow inputs to outputs. To this end we have
  a few soft rules such as:
        - Avoid mixins. Mixins introduce implicit dependencies and make it harder to reason about code.
        - Don't mess with metaclasses and double underscore methods without good reason.
          There is often an easier, clearer way to achieve the same result.

- No reinvention. We try to use well proven existing solutions before rolling our own. Hence the use
  of ``marshmallow`` for the ORM/serialization framework.

- No hijacking. Feather is complimentary or an 'add-on' to Falcon. It does not replace direct usage of Falcon (what
  you might expect from a framework). It solves some common use cases and provides some useful tools. When you want to
  do something unsupported and go direct to falcon, it doesnt get in your way.




