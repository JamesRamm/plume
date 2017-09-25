=====
Usage
=====

Feather lets you make `schemas` which are backed by MongoDB and then create falcon resources for these schemas.

Schemas
-------

Feather uses marshmallow ``Schema``'s to define MongoDB documents.
If you are not familiar with marshmallow, take a look at http://marshmallow.readthedocs.io/en/latest/index.html

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




