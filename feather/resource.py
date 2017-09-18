"""Resource classes for creating a JSON restful API.
"""
import json
import falcon

class Collection(object):
    """Generic class for listing/creating data via a schema
    """
    def __init__(self, uri_template, schema, methods=('get', 'post')):
        self._uri = uri_template
        self._schema = schema

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

    @uri_template.setter
    def uri_template(self, value):
        self._uri = value

    def make_error(self, resp, message, status=falcon.HTTP_BAD_REQUEST):
        resp.status = status
        resp.body = json.dumps({'message': message})
        resp.content_type = falcon.MEDIA_JSON

    def _get(self, req, resp):
        # dump all schema objects
        cursor = self._schema.find()
        result = self._schema.dumps(cursor, many=True)
        resp.body = result.data
        resp.content_type = falcon.MEDIA_JSON
        resp.status = falcon.HTTP_OK

    def _post(self, req, resp):
        # Handle JSON
        if req.content_type == 'application/json':
            data = req.bounded_stream.read()
            self._schema.post(data)
            resp.status = falcon.HTTP_CREATED
        else:
            self.make_error(resp, 'Unknown content type')


class Item(Collection):
    """Generic class for getting/editing a single data item via a schema
    """
    def __init__(self, uri_template, schema, methods=('get', 'patch', 'put', 'delete')):
        super(Item, self).__init__(uri_template, schema, methods)
        self._uri_param = uri_template.split('{')[1].split('}')[0]

    @Collection.uri_template.setter
    def uri_template(self, value):
        self._uri = value
        self._uri_param = value.split('{')[1].split('}')[0]

    def _get(self, req, resp, **kwargs):
        document = self._schema.get(kwargs)
        if document:
            result = self._schema.dumps(document)
            resp.body = result.data
            resp.content_type = falcon.MEDIA_JSON
            resp.status = falcon.HTTP_OK
        else:
            self.make_error(resp, 'No matches found')

    def _put(self, req, resp, **kwargs):
        if req.content_type == 'application/json':
            data = req.bounded_stream.read()
            self._schema.put(kwargs, data)
            resp.status = falcon.HTTP_ACCEPTED
        else:
            self.make_error(resp, 'Unknown content type')

    def _patch(self, req, resp, **kwargs):
        if req.content_type == 'application/json':
            data = req.bounded_stream.read()
            self._schema.patch(kwargs, data)
            resp.status = falcon.HTTP_ACCEPTED
        else:
            self.make_error(resp, 'Unknown content type')

    def _delete(self, req, resp, **kwargs):
        self._schema.delete(kwargs)
