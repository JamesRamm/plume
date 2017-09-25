.. api:

API Reference
==============

Schemas and fields
------------------

Inherit from ``MongoSchema`` to start creating schemas which are materialized to MongoDB.
A ``MongoSchema`` is just a marshmallow schema with extra functions to give it ORM-like abilities.

.. automodule:: feather.schema
    :members:


Some useful fields for using marshmallow as a MongoDB ORM are also provided.

.. automodule:: feather.fields
    :members:


Resources and hooks
--------------------

.. automodule:: feather.resource
    :members:


.. automodule:: feather.hooks
    :members:


Storage
--------

.. automodule:: feather.storage
    :members:


Connecting to a database
--------------------------

.. automodule:: feather.connection
    :members:
