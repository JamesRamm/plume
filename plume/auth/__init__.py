from datetime import datetime, timedelta
import json

import falcon
import jwt

from plume.auth.middleware import AuthMiddleware
from plume.auth.resource import LoginResource


class AuthHandler:
    """Handles authentication and authorization using JWT.

    The AuthHandler provides both a "Login" resource and an authentication
    middleware.

    The AuthHandler encapsulates both these concepts to provide common
    functionality (JWT encoding/decoding and user serialization) to both.

    Usage:

        # Create an instance of the handler with your own user_model
        auth = AuthHandler(user_model, id_field="email")
        # Register the login resource and middleware with your app
        auth_mw = auth.middleware()
        login = auth.login_resource("route")
        api = create_app([login], [auth_mw])

        # Instead of using plumes' `create_app` you can do:
        api = falcon.API(middleware=[auth_mw])
        api.add_route(login.uri_template, login)

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
    def __init__(self, user_model, id_field="email", password_field="password", secret_key=None, token_algorithm='HS256', password_checker=None):
        self._user_model = user_model
        self._id_field = id_field
        self._secret_key = secret_key or 'secretkey'
        self._algo = token_algorithm
        self._pass_field = password_field

        if not password_checker:
            try:
                from passlib.hash import sha256_crypt
                self._pass_check = sha256_crypt.verify
            except ImportError:
                raise AttributeError(
                    "You need to explicitly pass a password_checker argument or"
                    " install passlib to use the default"
                )
        else:
            self._pass_check = password_checker

    def login_resource(self, route):
        return LoginResource(route, self)

    def middleware(self):
        return AuthMiddleware(self, (LoginResource, ))

    def _get_user(self, userid):
        """Get user details from the database
        """
        cursor = self._user_model.get({self._id_field: userid})
        return self._user_model.dumps(cursor)

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
        print(user)
        if user and self._pass_check(password, user[self._pass_field]):
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
