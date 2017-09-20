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



Example
--------

The following example creates a basic JSON API for a representation of a user.

.. code-block:: python

    from datetime import datetime
    from feather import create_app, schema, Collection, Item
    from feather import connect
    from marshmallow import fields, Schema

    class UserSchema(schema.MongoSchema):
        """Example user schema for testing.

        The ``MongoSchema`` base class provides methods to
        save the validated data to the mongodb backend.
        The regular ``Schema`` from marshmallow is untouched - you
        can use ``loads`` and ``dumps`` without any interaction with the db.
        Instead ``MongoSchema`` introduces the following methods:

        ``post``: Create a new document
        ``patch``: Update a document
        ``put``: Replace a document
        ``get``: Retrieve a single document
        ``find``: Filter the documents

        These methods use ``pymongo`` directly for speed and provide a simple, yet powerful
        way of providing an ORM *and* serializer in one class.
        You can pass the result of ``get`` and ``find`` directly to ``dumps``:

                document = schema.get({'email': 'bob@testerson.com'})
                schema.dumps(document)

                # Get all documents
                schema.dumps(schema.find(), many=True)

        By utilizing marshmallow, you don't need to learn yet another library/ORM - simply
        declare fields as you would with marshmallow.
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

    user = UserSchema()

    # ``Collection`` and ``Item`` are falcon Resource classes which provide the HTTP method handlers.
    # They are designed to work with the schema passed into them on creation - a basic CRUD JSON API
    # can be created with no extra configuration.
    # You pass the URI template (that would normally be passed to ``api.add_route`` in falcon) directly
    # to the resource class. This keeps your code DRY and minimal.
    # With a ``Collection`` resource we can post and retrieve a list of all user documents.
    # An ``Item`` resource allows retrieving a single item (in this case the user), updating and
    # deleting.
    # The ``create_app`` function registers your routes & resources with falcon and returns the ``API``
    # instance.
    resources = (Collection(user, '/users'), Item(user, '/users/{email}'))

    api = create_app(resources)

    # We also need to connect to the database. The ``connect`` function takes the same
    # arguments as pymongo's ``MongoClient``. Here we connect to localhost.
    connect()




