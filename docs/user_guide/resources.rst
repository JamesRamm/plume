=========
Resources
=========

Default ``Collection`` and ``Item`` resources are provided to easily provide endpoints for your schemas.
Each resource has the following features:

- Schema instances are passed into the resource for it to work on
- URI template is encapsulated in the resource
- Restricting the HTTP methods it will handle
- Changing the content types it will accept
- Custom error handlers for schema validation errors

A ``Collection`` resource by default provides POST and GET handlers, with GET returning a JSON
list of the requested resource.
An ``Item``

Using the ``Person`` schema we created in the previous chapter, we can declare our resources:

..  code-block:: python

    from plume import Collection, Item

    person = Person()

    resources = (
        Collection(person, '/people'),
        Item(person, '/people/{name}')
    )

With the resources ready, you can use a factory function to create a Falcon app:


..  code-block:: python

    from plume import create_app

    # ``application`` is an instance of ``falcon.API``
    application = create_app(resources)

All ``create_app`` does is instantiate an app and call Falcons' ``add_route`` for each resource in the given list.


File Storage
--------------

Plume also provides basic ``FileCollection`` and ``FileItem`` resource classes, specifically intended
for serving and accepting file data.
As with ``Collection`` and ``Item`` resources, you can configure the uri template, allowed content types and
HTTP methods.
You also expected to pass a storage class to the resource. This is essentially the same as in the Falcon tutorial_.

The storage class should provide ``save``, ``open`` and ``list`` methods.
``save`` and ``open`` are fairly clear and are as explained in the falcon tutorial.
``list`` should return the URL's of all available files in the store.

Plume provides a basic file store - ``plume.FileStore`` which can be used.

All this makes it easy to add file handling. Expanding the resources example:


..  code-block:: python

    import os
    from plume import Collection, Item, FileCollection, FileItem, FileStore

    # Setup the storage
    path = os.path.dirname(__file__)
    store = FileStore(path)

    person = Person()

    resources = (
        Collection(person, '/people'),
        Item(person, '/people/{name}'),
        FileCollection(store), # The uri_template argument defaults to ``/files``
        FileItem(store)
    )

Handling files in schemas
++++++++++++++++++++++++++

If you come from django, you might be expecting some sort of ``FileField`` you can declare on a schema.
Plume does not provide this; This keeps your file storage logic completely separate from the rest of the app,
meaning you could potentially swap out your file store for a GridFS backed store, or switch to a completely
different service for hosting files.

I reccomend that you declare files as Url fields on your schema, with the ``relative=True`` parameter set.

The other advantage over tighter coupling is that your file fields could simply be a URL to an entirely different website
(e.g. some stock image provider, or a facebook profile picture).

There are disadvantages which we need to overcome:

- You now need to make 2 requests from a client. One to upload the file and one to update the resource with the file url.
    (It is a matter of some debate as to whether this should in fact be considered the best practice for REST API's since
     multipart form data is not truly JSON or XML)

- Plume offers no validation or method by which to link a file upload to a subsequent patch request other than
  what the client tells it. E.g. imagine a client successfully uploads the file but the patch to update the resource with the
  new URL goes wrong. To overcome this, you could take a look at 'Resumable Uploads'.
  We will be looking at whether Plume can provide any nice api to help with this in the future.

.. _tutorial: https://falcon.readthedocs.io/en/stable/user/tutorial.html#serving-images