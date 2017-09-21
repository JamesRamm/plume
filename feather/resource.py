"""Resource classes for creating a JSON restful API.
"""
import mimetypes
import falcon
import simplejson
from feather.hooks import validate_content_type

class FeatherResource(object):
    """Base class used for setting a uri_template, allowed content types
    and HTTP methods provided.

    By encapsulating the URI, we can provide factory methods
    for routing, allowing us to specify the resource and its' uri
    in one place
    """
    def __init__(
            self,
            uri_template,
            content_types=('application/json',),
            methods=('get', 'patch', 'put', 'delete', 'post')
    ):
        self._uri = uri_template
        self._content_types = content_types

        # We dynamically set attributes for the expected
        # falcon HTTP method handlers.
        # This allows the user of ``Resource`` to define a subset
        # of methods to use. E.g. if they dont want to support
        # 'on_post', this would be left off the method list
        for method in methods:
            method_name = 'on_{}'.format(method)
            handler = getattr(self, '_{}'.format(method))
            setattr(self, method_name, handler)

    @property
    def uri_template(self):
        """The URI for this resource
        """
        return self._uri

    @property
    def allowed_content_types(self):
        return self._content_types

    def _post(self, req, resp):
        pass

    def _get(self, req, resp):
        pass

    def _put(self, req, resp):
        pass

    def _patch(self, req, resp):
        pass

    def _delete(self, req, resp):
        pass



class Collection(FeatherResource):
    """Generic class for listing/creating data via a schema

    Using falcons before/after decorators.
    ++++++++++++++++++++++++++++++++++++++

    Remembering that the @ operator is just syntactic sugar,
    if we want to apply a decorator we could do it with minimal effort like this:

        resource = Collection(...)
        resource.on_post = falcon.before(my_function)(resource.on_post)

    Alternatively, we could create a subclass:

        class MyResource(Collection):
            on_post = falcon.before(my_function)(Collection.on_post.__func__)
    """
    def __init__(
            self,
            schema,
            uri_template,
            content_types=('application/json'),
            methods=('get', 'post')
    ):
        super(Collection, self).__init__(uri_template, content_types, methods)
        self._schema = schema



    def _get(self, req, resp):
        # dump all schema objects
        cursor = self._schema.find()
        result = self._schema.dumps(cursor, many=True)
        resp.body = result.data
        resp.content_type = falcon.MEDIA_JSON
        resp.status = falcon.HTTP_OK

    @falcon.before(validate_content_type)
    def _post(self, req, resp):
        data = req.bounded_stream.read()
        complete_data, errors = self._schema.post(data)
        resp.status = falcon.HTTP_CREATED

class Item(FeatherResource):
    """Generic class for getting/editing a single data item via a schema
    """
    def __init__(
            self,
            schema,
            uri_template,
            content_types=('application/json'),
            methods=('get', 'patch', 'put', 'delete')
    ):
        super(Item, self).__init__(uri_template, content_types, methods)
        self._schema = schema

    def _get(self, req, resp, **kwargs):
        document = self._schema.get(kwargs)
        if document:
            result = self._schema.dumps(document)
            resp.body = result.data
            resp.content_type = falcon.MEDIA_JSON
            resp.status = falcon.HTTP_OK
        else:
            raise falcon.HTTPUnsupportedMediaType('Expected application/json')

    @falcon.before(validate_content_type)
    def _put(self, req, resp, **kwargs):
        data = req.bounded_stream.read()
        self._schema.put(kwargs, data)
        resp.status = falcon.HTTP_ACCEPTED
        resp.location = self.uri_template.format(**kwargs)

    @falcon.before(validate_content_type)
    def _patch(self, req, resp, **kwargs):
        data = req.bounded_stream.read()
        self._schema.patch(kwargs, data)
        resp.status = falcon.HTTP_ACCEPTED
        resp.location = self.uri_template.format(**kwargs)

    def _delete(self, req, resp, **kwargs):
        self._schema.delete(kwargs)
        resp.status = falcon.HTTP_ACCEPTED


class FileCollection(FeatherResource):
    """Collection for posting/listing file uploads.
    """
    def __init__(self, store, uri_template='/files', content_types=None, methods=('get', 'post')):
        super(FileCollection, self).__init__(uri_template, content_types, methods)
        self._store = store

    def _get(self, req, resp):
        uploads = self._store.list()
        resp.body = simplejson.dumps(uploads)
        resp.status = falcon.HTTP_200

    @falcon.before(validate_content_type)
    def _post(self, req, resp):
        name = self._store.save(req.stream, req.content_type)
        resp.status = falcon.HTTP_CREATED
        resp.location = "{}/{}".format(self._uri, name)


class FileItem(FeatherResource):
    """Item for downloading a single file
    """
    def __init__(self, store, uri_template='/files/{name}', content_types=None, methods=('get',)):
        super(FileItem, self).__init__(uri_template, content_types, methods)
        self._store = store
        self._uri_param = self._uri.split('{')[1].split('}')[0]

    def _get(self, req, resp, **kwargs):
        name = kwargs[self._uri_param]
        resp.content_type = mimetypes.guess_type(name)[0]
        resp.stream, resp.stream_len = self._store.open(name)
