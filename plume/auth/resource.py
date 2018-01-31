import simplejson
import falcon
from plume.resource import PlumeResource

class LoginResource(PlumeResource):

    def __init__(self, uri_template, auth_handler):
        self.auth_handler = auth_handler
        super(LoginResource, self).__init__(uri_template, methods=('post',))

    def _post(self, req, resp):
        data = req.bounded_stream.read()
        data = simplejson.loads(data)
        token = self.auth_handler.login(data)
        resp.body = simplejson.dumps({'token': token})
