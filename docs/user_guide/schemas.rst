=======
Schemas
=======


Feather uses marshmallow ``Schema``'s to define MongoDB documents.
If you are not familiar with marshmallow, take a look at http://marshmallow.readthedocs.io/en/latest/index.html
The schema integrates with pymongo in order to deliver data to and from the database. To keep this efficient,
the pymongo integration is very light; it is worth being familiar with pymongo if you need to do more complex
database logic.

A feather schema is defined exactly like a marshmallow schema except it inherits from ``MongoSchema``.
This provides a few new methods which will both materialize schema data to the database and get documents
from the database.

Here is an example of defining a schema:

..  code-block:: python

    from feather import schema
    from marshmallow import fields

    class Person(schema.MongoSchema):

        name = fields.Str()
        email = fields.Str(required=True)


Like a regular marshmallow schema, you can call ``dumps`` and ``loads`` to serialize and deserialize data.
You can do this safely with no impact on the database (just like marshamllow). In order to save/get data from
the database, Feather provides new methods and resource classes to work directly with these methods.

Since the schema will be backed by MongoDB, we must connect before creating an instance:

.. code-block:: python

    from feather import connection

    # Without arguments we connect to the default database on localhost
    client = connect()
    person = Person()

Database constraints
--------------------

Feather schemas have support for creating constraints on the database. These are defined in the marshmallow
``Meta`` options class:


.. code-block:: python

    import simplejson
    from feather import schema
    from marshmallow import fields

    class Person(schema.MongoSchema):

        class Meta:
            json_module = simplejson
            constraints = (('email', {'unique': True}), ('name', {}))

        name = fields.Str()
        email = fields.Str(required=True)


The constraints are specified as an iterable of 2-tuples, each comprising a 'key' and a dictionary of
keyword arguments passed directly to pymongos' ``create_index``.
This requires you to know a little about how ``create_index`` works (https://api.mongodb.com/python/current/api/pymongo/collection.html#pymongo.collection.Collection.create_index)
but has the advantage of being able to easily and transparently support all indexing possibilities.

Nested Documents & Relations
----------------------------

You can represent nested documents using marshmallows ``Nested`` field.
The schema you intend to nest can just inherit directly from ``Schema`` since the parent schema
will handle its' creation:

.. code-block:: python

    import simplejson
    from feather import schema
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

Further Usage
----------------

- Feather supplies a small number of extra fields for use with your schemas, such as ``Choice``, ``Slug`` and ``MongoId``.
- If you wish to interact with the pymongo ``collection`` instance directly, you can call ``get_collection`` on any
class inheriting from ``MongoSchema``.
- By implementing the ``get_filter`` method on your schema class, you can provide per request
 filtering. Coupled with appropriate middleware, this can let you restrict/modify the queryset
 by user characteristics.


