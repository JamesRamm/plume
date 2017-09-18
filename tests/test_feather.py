import json
import codecs
import pytest
import falcon
from falcon import testing

from feather.connection import connect, disconnect
from .app import create, UserSchema

API = create()

@pytest.fixture
def client():
    client = connect(database='test')
    yield testing.TestClient(API)
    # Drop the test database
    client.drop_database('test')
    disconnect()


# pytest will inject the object returned by the "client" function
# as an additional parameter.
class TestUsers:

    _fake_user = {
        'name': 'Bob Testerson',
        'email': 'bob@bob.com',
        'profile': {
            'biography': 'My name is Bob',
            'profileImage': 'http://somewhere.com/some_image.png'
            }
        }

    def _make_user(self):
        data = UserSchema().post(json.dumps(self._fake_user))
        return data

    def test_list_users(self, client):
        doc = self._make_user()
        response = client.simulate_get('/users')
        result_doc = json.loads(response.content.decode('utf-8'))
        assert doc['name'] == result_doc[0]['name']
        assert doc['email'] == result_doc[0]['email']
        assert result_doc[0]['slug']
        assert doc['profile']['biography'] == result_doc[0]['profile']['biography']
        assert response.status == falcon.HTTP_OK

    def test_get_user(self, client):
        doc = self._make_user()
        response = client.simulate_get('/users/{}'.format(doc['email']))
        assert response.status == falcon.HTTP_OK

    def test_post_users(self, client):
        doc = json.dumps(self._fake_user)
        response = client.simulate_post(
            '/users',
            body=doc,
            headers={'content-type': 'application/json'}
        )

        assert response.status == falcon.HTTP_CREATED

    def test_patch_user(self, client):
        doc = self._make_user()
        data = json.dumps({'name': 'Different Name'})
        response = client.simulate_patch(
            '/users/{}'.format(doc['email']),
            body=data,
            headers={'content-type': 'application/json'}
        )
        assert response.status == falcon.HTTP_ACCEPTED
