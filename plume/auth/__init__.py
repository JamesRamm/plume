from datetime import datetime, timedelta
import json

import falcon
import jwt
from passlib.hash import sha256_crypt

from plume.auth.middleware import AuthMiddleware
from plume.auth.resource import LoginResource, RegistrationResource


class AuthHandler:
    """Handles authentication and authorization using JWT.

    The AuthHandler provides both a defaulut "Login" and "Registration" resource and a matching
    authorization middleware.

    The AuthHandler encapsulates both these concepts to provide common
    functionality (JWT encoding/decoding and user serialization) to both.

    Args:

        login_resource (PlumeResource): As resource class instance which will handle POST login requests. This will be exempt from authorization
        registration_resource (PlumeResource): As resource class instance which will handle POST registration requests. This will be exempt from authorization

    Usage:

        # Create an instance of the handler with your own user_model
        auth = AuthHandler(user_model, id_field="email")
        # Register the login & registration resource and middleware with your app
        auth_mw = auth.middleware()
        login = auth.login_resource("/login")
        register = auth.registration_resource("/register")

        # Create the falcon app
        api = create_app([login, register], middleware = [auth_mw])

        # Remember, the create app function is essentially a wrapper for the following:
        api = falcon.API(middleware=[auth_mw])
        api.add_route(login.uri_template, login)
        api.add_route(register.uri_template, register)

    A successful request to the login route will receive a json web token in the 'token' field of
    the response body. This token should be used in the 'Authorization' header for subsequent
    requests. Successful authorization will result in the user data being added to the request
    `context`.

    ## Customisation
    You can customise the login resource used by inheriting from AuthHandler overriding
    `login_resource` and the middleware by overriding `middleware`.
    If you wish to have a different mechanism for retrieving the user details (e.g for
    storing user data in something other than MongoDB) you can override `_get_user`.
    This method should return a simple python dictionary.



    """
    def __init__(
        self,
        user_model,
        id_field="email",
        password_field="password",
        secret_key=None,
        token_algorithm='HS256',
        password_checker=sha256_crypt,
        login_resource=None,
        registration_resource=None):
        self._user_model = user_model
        self._id_field = id_field
        self._secret_key = secret_key or 'secretkey'
        self._algo = token_algorithm
        self._pass_field = password_field
        self._pass_check = password_checker

        self._login_resource = login_resource
        self._registration_resource = None

    def login_resource(self, route):
        """Get the login resource instance for this auth handler
        """
        if not self._login_resource:
            self._login_resource = LoginResource(route, self)
        return self._login_resource

    def registration_resource(self, route):
        if not self._registration_resource:
            self._registration_resource = RegistrationResource(self._user_model, route)
        return self._registration_resource

    def middleware(self, exempt = None):
        """Get the middleware for authorization.
        By default, the login and registration resources are exempt
        """
        default_exempt = [self._login_resource.__class__, self._registration_resource.__class__]
        if exempt:
            default_exempt.extend(exempt)
        return AuthMiddleware(self, default_exempt)

    def _get_user(self, userid):
        """Get user details from the database
        """
        cursor = self._user_model.get({self._id_field: userid})
        result = self._user_model.dump(cursor)
        return result.data

    def _hash_password(self, password):
        return self._pass_check.hash(password)

    def login(self, request_data):
        """Authenticate a user given authentication data and returns an authorization token
        (json web token).

        Raises HTTPUnauthorized if passwords dont match or the user doesnt exist
        and HTTPBadRequest if the given data is
        invalid.
        """
        try:
            userid = request_data[self._id_field]
            password = request_data[self._pass_field]
        except KeyError:
            return falcon.HTTPBadRequest(
                'Password and {} should be submitted in request data'.format(self._id_field)
            )

        user = self._get_user(userid)
        if user and self._pass_check.verify(password, user[self._pass_field]):
            return self.create_jwt(userid)
        else:
            raise falcon.HTTPUnauthorized('Bad email/password combination, please try again')

    def create_jwt(self, userid):
        """Creates a JSON Web Token for a given userid
        """
        return jwt.encode({'userid': userid},
                          self._secret_key,
                          algorithm=self._algo).decode("utf-8")

    def validate_jwt(self, token):
        try:
            payload = jwt.decode(token, self._secret_key, verify='True', algorithms=[self._algo])
            return self._get_user(payload["userid"])
        except jwt.DecodeError:
            return False
