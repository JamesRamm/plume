=======
Schemas
=======


Plume builds upon marshmallow's ``Schema`` class both for serialization and as a lightweight 'ODM' (Object-Document Mapper) to MongoDB.
If you are not familiar with marshmallow, take a look at the documentation_.

A plume schema is defined exactly like a marshmallow schema except it inherits from ``MongoSchema``.
This provides a few new methods which will both materialize schema data to the database and get documents
from the database.

``MongoSchema`` uses pymongo_ in order to deliver data to and from the database. To keep this efficient,
the pymongo integration is simmple and streamlined, with pymongo objects being readily accessible from
various ``MongoSchema`` methods. As such it is worth being familiar with pymongo_ if you need to do more complex
database logic.

Here is an example of defining a schema:

..  code-block:: python

    from plume import schema
    from marshmallow import fields

    class Person(schema.MongoSchema):

        name = fields.Str()
        email = fields.Str(required=True)


Like a regular marshmallow schema, you can call ``dumps`` and ``loads`` to serialize and deserialize data.
You can do this safely with no impact on the database (just like marshamllow). In order to save/get data from
the database, Plume provides new methods and resource classes to work directly with these methods.

Since the schema will be backed by MongoDB, we must connect before creating an instance:

.. code-block:: python

    from plume import connection

    # Without arguments we connect to the default database on localhost
    client = connect()
    person = Person()

Database constraints
--------------------

Plume schemas have support for creating constraints on the database. These are defined in the
``Meta`` options class:

.. code-block:: python

    import simplejson
    from plume import schema
    from marshmallow import fields

    class Person(schema.MongoSchema):

        class Meta:
            json_module = simplejson
            constraints = (('email', {'unique': True}), ('name', {}))

        name = fields.Str()
        email = fields.Str(required=True)


The constraints are specified as an iterable of 2-tuples, each comprising a 'key' and a
dictionary of keyword arguments passed directly to pymongos' ``create_index``.
This requires you to know a little about how ``create_index`` works_ but has the advantage
of being able to easily and transparently support all indexing possibilities.

Nested Documents & Relations
----------------------------

You can represent nested documents using marshmallows ``Nested`` field.
The schema you intend to nest can just inherit directly from ``Schema`` since the parent
schema will handle its' creation:

.. code-block:: python

    import simplejson
    from plume import schema
    from marshmallow import fields, Schema

    class Person(schema.MongoSchema):

        class Meta:
            json_module = simplejson
            constraints = (('email', {'unique': True}), ('name', {}))

        name = fields.Str()
        email = fields.Str(required=True)
        profile = fields.Nested('Profile')


    class Profile(Schema):

        biography = fields.Str()
        ...

MongoDB does not support foreign keys, nor does pymongo create abstractions for relations
such as many to many, one to one etc.
In my view, this is a good thing. Handling relations at the app level allows for a more app-specific
implementation. It allows us to:

- Keep apps completely decoupled at the database level, making it easier to drop certain schemas
  for different situations. E.g. if we were to split our app into microservices, switch to using a 3rd party
  service for some part of the app or simply refactor into a different structure

- We generally know more about what is and isn't acceptable to be missing/broken at an app level.
  I have often had to deal with painful migrations due to complex relationships between apps, when
  the front-end could actually be easily modified to be agnostic as to whether some data appears or not.

- We can choose which field of the related data to use for our relation. For example, imagine we are representing
  a client-supplier relationship. The supplier has a list of clients they deal with.
  We may decide as a first iteration that we only wish to simply let the supplier see a list of client emails.
  We can simply use a ``List`` field and embed the emails right in the supplier schema. We have represented the
  relationship but we don't need any complex joins and lookups to fetch the data.
  At a later date we may wish to give the client a full profile. We can simply keep the suppliers list of emails
  and create a new schema representing a client profile, with an index on the email field.
  The front-end can now - either work as normal (just showing a list of emails), or make a second call to
  fetch the client profile for each email.
  You might then decide there is little business value in having the client profile, so lets try dropping it for
  a month and get some feedback.
  All this kind of stuff is much easier to do when you handle relations at app level rather than database level.

In short, define your relations and rules within your app.

Further Usage
----------------

- Plume supplies a small number of extra fields for use with your schemas, such as ``Choice``, ``Slug`` and ``MongoId``.
- If you wish to interact with the pymongo ``collection`` instance directly, you can call ``get_collection`` on any
  class inheriting from ``MongoSchema``.
- By implementing the ``get_filter`` method on your schema class, you can provide per request
  filtering. Coupled with appropriate middleware, this can let you restrict/modify the queryset
  by user characteristics.


.. _pymongo: https://api.mongodb.com/python/current/index.html
.. _documentation: http://marshmallow.readthedocs.io/en/latest/index.html
.. _works: https://api.mongodb.com/python/current/api/pymongo/collection.html#pymongo.collection.Collection.create_index