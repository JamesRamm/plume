=====
Usage
=====

Feather is a library to help you quickly make Falcon applications backed by MongoDB, Elasticsearch, both, or more!
Feather is *not* a framework - you can use it alongside regular Falcon usage as much or as little as you want.
It makes no assumptions and doesn't require you to do things in a certain style. Like all good libraries,
it aims to be a carefully crafted collection of functions and classes to make it easier to craft a streamlined webapp.

Feather allows you to:

- Specify your MongoDB documents as regular Marshmallow schemas. This provides data serialization, validation and
a lightweight ORM all in one place!

- Easily create falcon resources for your schemas. Just one line of code is necessary.

- Easily create a falcon app based on your resources.

It's easiest to explain each of those points with some simple examples.

Specifying your schemas
------------------------

A schema is a regular Marshmallow schema which inherits from ``MongoSchema``. Apart from the inheritance,
you pretty much declare it like any Marshmallow schema:

.. code-block:: python

    import simplejson
    from marshmallow import fields
    from feather.schema import MongoSchema
    from feather.connection import connect
    from feather import create_app, Collection, Item

    class Person(MongoSchema):

        class Meta:
            json_module = simplejson
            constraints = (('field', {}), ('email', {'unique': True}))

        name = fields.Str()
        email = fields.Email(required=True)

You can interact with it as any marshmallow schema - using ``loads`` and ``dumps`` will not affect the MongoDB database.
``MongoSchema`` provides a few new methods which will use marshmallow to serialize/deserialize and validate the data and
and save (or retrieve) it from MongoDB.
Note the ``constraints`` option. This is to specify which fields should have indexes created.

Creating resources
------------------

Feather provides a ``Collection`` and an ``Item`` resource class, which are designed to work with
any ``MongoSchema`` schema. They provide the full CRUD operation set (see http://www.restapitutorial.com/lessons/httpmethods.html).
You simply pass your schema and the route you want to use to them:

.. code-block:: python

    connect()
    person = Person()
    resources = (Collection('/people', person), Item('/people/{email}', person))


The ``connect`` function takes the same arguments as pymongo's ``MongoClient`` and must be called once before creating a schema instance.

Creating the app
----------------

You can use the ``create_app`` factory method to route all the resources, instead of typing it all out again:

.. code-block:: python

    api = create_app(resources)

