import json
import falcon
from plume.resource import PlumeResource

class LoginResource(PlumeResource):

    def __init__(self, uri_template, auth_handler):
        self.auth_handler = auth_handler
        super(LoginResource, self).__init__(uri_template, methods=('post',))

    def _post(self, req, resp):

        req_stream = req.stream.read()
        if isinstance(req_stream, bytes):
            data = json.loads(req_stream.decode())
        else:
            data = json.loads(req.stream.read())

        token = self.auth_handler.login(data)
        resp.body = json.dumps({'token': token})
