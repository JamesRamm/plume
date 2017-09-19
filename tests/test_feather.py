import json
import os

import pytest
import falcon
from falcon import testing

from feather.connection import connect, disconnect
from feather import FileCollection, FileStore
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


class TestFileResource:

    def create_resource(self):
        # Create the file store and resource
        path = os.path.dirname(__file__)
        store = FileStore(path, namegen=lambda: '0xa6a6a6')
        resource = FileCollection(store)
        API.add_route(resource._uri, resource)
        return store

    def test_posted_image_gets_saved(self, client):

        # Create the file store and resource
        store = self.create_resource()

        # When the service receives an image through POST...
        fake_image_bytes = b'fake-image-bytes'
        response = client.simulate_post(
            '/files',
            body=fake_image_bytes,
            headers={'content-type': 'image/png'}
        )

        # ...it must return a 201 code, save the file, and return the
        # image's resource location.
        assert response.status == falcon.HTTP_CREATED
        assert response.headers['location'] == '/files/0xa6a6a6.png'

        expected_path = os.path.join(store._storage_path, "0xa6a6a6.png")
        assert os.path.exists(expected_path)
        os.unlink(expected_path)

    def test_list_files(self, client):
        store = self.create_resource()
        # create an image
        name = store._namegen()
        filename = "{}.png".format(name)
        path = os.path.join(store._storage_path, filename)
        with open(path, 'wb') as fobj:
            fobj.write(b'fake image')

        response = client.simulate_get(
            '/files'
        )
        result_doc = json.loads(response.content.decode('utf-8'))
        assert response.status == falcon.HTTP_200
        assert filename in result_doc
        os.unlink(path)

    def test_can_download(self, client):
        pass
