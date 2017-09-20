
Recipes
=======


Wrapping serialized results
----------------------------

By default, the output from serialization is simply a JSON object (if serializing a single model) or
array (for many models). e.g.:

.. code-block:: json

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

.. code-block:: json

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

class Person(MongoSchema):

    name = field.Str()
    email = field.Str()

    @post_dump(pass_many=True)
    def wrap_with_envelope(self, data, many):
        return {data: data, meta: {...}, errors: [...]}