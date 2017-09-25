.. api:

API Reference
==============

Schemas and fields
------------------

Inherit from ``MongoSchema`` to start creating schemas which are materialized to MongoDB.
A ``MongoSchema`` is just a marshmallow schema with extra functions to give it ORM-like abilities.

.. automodule:: plume.schema
    :members: MongoSchema


Some useful fields for using marshmallow as a MongoDB ORM are also provided.

.. automodule:: plume.fields
    :members:


Resources and hooks
--------------------

.. automodule:: plume.resource
    :members:


.. automodule:: plume.hooks
    :members:


Storage
--------

.. automodule:: plume.storage
    :members:


Connecting to a database
--------------------------

.. automodule:: plume.connection
    :members:
