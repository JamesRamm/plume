import falcon
import jwt

class AuthMiddleware(object):
    def __init__(self, auth_handler, exempt_resources=[]):
        self._auth_handler = auth_handler
        self._exempt = exempt_resources

    def process_resource(self, req, resp, resource, params): # pylint: disable=unused-argument
        if self._exempt and isinstance(resource, self._exempt):
            # No token necessary for the login route
            return

        token = req.get_header("Authorization", required=True)

        challenges = ['authorization_uri="/login"']
        if token is None:
            description = ('Please provide an json web token '
                           'as part of the request.')

            raise falcon.HTTPUnauthorized('Auth token required',
                                          description,
                                          challenges,
                                          href='http://docs.example.com/auth')

        user = self._auth_handler.validate_jwt(token)
        if not user:
            description = ('The provided auth token is not valid. '
                           'Please request a new token and try again.')

            raise falcon.HTTPUnauthorized('Authentication required',
                                          description,
                                          challenges,
                                          href='http://docs.example.com/auth')

        else:
            # If we get this far we are authorized
            req.context["user"] = user
