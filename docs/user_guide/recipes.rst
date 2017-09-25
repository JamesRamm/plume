
Recipes
=======


Wrapping serialized results
----------------------------

By default, the output from serialization is simply a JSON object (if serializing a single model) or
array (for many models). e.g.:

..  code-block:: javascript

    [
        {
            'name': 'John Cleese',
            'email': 'john.cleese@fake.com'
        },

        {
            'name': 'Michael Palin',
            'email': 'micahel.palin@fake.com'
        }
    ]

However, we may wish to return a 'wrapped' response, e.g:

..  code-block:: javascript

    {
        'meta': {},
        'errors': [],
        'data': [
                    {
                        'name': 'John Cleese',
                        'email': 'john.cleese@fake.com'
                    },

                    {
                        'name': 'Michael Palin',
                        'email': 'micahel.palin@fake.com'
                    }
                ]
    }

We can use marshmallows' ``post_dump`` decorator to achieve this in our schema:

..  code-block:: python

    class Person(MongoSchema):

        name = field.Str()
        email = field.Str()

        @post_dump(pass_many=True)
        def wrap_with_envelope(self, data, many):
            return {data: data, meta: {...}, errors: [...]}

Filtering output per user
--------------------------

We want to filter/modify the responses of GET requests depending on the connected user.

You can provide a ``get_filter`` method on the schema definition which accepts a falcon ``Request``
object and returns a dictionary of keyword arguments compatible with pymongos' ``find`` method:

..  code-block:: python

    class MySchema(MongoSchema):

        ...

        def get_filter(self, req):
            return {
                'filter': {<the desired filter params>},
                'projection': (<subset of fields to include in the returned documents>)
            }


In order to customise ``get_filter`` for each user, the ``Request`` object needs to have some useful information
attached. This is where we would make use of Falcons' middleware in order to attach information
about the user. For example, you could use falcon-auth_
to add the user to your request.
A 'loader' function for ``falcon-auth`` (see the falcon-auth readme) might look something like:

.. code-block: python

    def user_loader(username, password):

        schema = MyUserSchema()
        # First get the document matching the username
        document = schema.get({'username': username})

        # Now check the password
        if document and document.password == some_hash_function(password):
            # we could return the 'raw' pymongo document...
            return document
            # Or serialize it to native python types..
            # return schema.dump(document)



We can now access ``req.context['user']`` in our ``get_filter``:

..  code-block:: python

    class MySchema(MongoSchema):

        # Username of the 'owner' of this document
        owner = fields.Str()

        ...

        def get_filter(self, req):
            user = req.context['user']
            if user
            return {
                'filter': {'owner': user['username']},
            }


.. _falcon-auth: https://github.com/loanzen/falcon-auth