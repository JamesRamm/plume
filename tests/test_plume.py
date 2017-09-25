import json
import os

import pytest
import falcon
from falcon import testing

from plume.connection import connect, disconnect, get_database
from plume import FileCollection, FileItem, FileStore
from plume.storage import unique_id
from .app import create, UserSchema, FilterSchema

@pytest.fixture
def client():
    conn = connect(database='test')
    yield testing.TestClient(create())
    # Drop the test database
    conn.drop_database('test')
    disconnect()


FAKE_USER = {
    'name': 'Bob Testerson',
    'email': 'bob@bob.com',
    'profile': {
        'biography': 'My name is Bob',
        'profileImage': 'http://somewhere.com/some_image.png'
        }
    }

# pytest will inject the object returned by the "client" function
# as an additional parameter.
class TestUsers:

    def _make_user(self):
        data, errors = UserSchema().post(json.dumps(FAKE_USER))
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
        doc = json.dumps(FAKE_USER)
        response = client.simulate_post(
            '/users',
            body=doc,
            headers={'content-type': 'application/json'}
        )

        assert response.status == falcon.HTTP_CREATED

    def test_post_duplicate(self, client):
        doc = json.dumps(FAKE_USER)
        response = client.simulate_post(
            '/users',
            body=doc,
            headers={'content-type': 'application/json'}
        )

        response = client.simulate_post(
            '/users',
            body=doc,
            headers={'content-type': 'application/json'}
        )
        assert response.status == falcon.HTTP_CONFLICT

    def test_post_bad_data(self, client):
        doc = json.dumps({'email': 'bad email'})
        response = client.simulate_post(
            '/users',
            body=doc,
            headers={'content-type': 'application/json'}
        )
        assert response.status == falcon.HTTP_BAD_REQUEST

    def test_post_bad_content_type(self, client):
        doc = json.dumps(FAKE_USER)
        response = client.simulate_post(
            '/users',
            body=doc,
            headers={'content-type': 'absolute rubbish'}
        )
        assert response.status == falcon.HTTP_415

    def test_patch_bad_content_type(self, client):
        doc = self._make_user()
        response = client.simulate_patch(
            '/users/{}'.format(doc['email']),
            body="",
            headers={'content-type': 'absolute rubbish'}
        )
        assert response.status == falcon.HTTP_415

    def test_patch_user(self, client):
        doc = self._make_user()
        data = json.dumps({'name': 'Different Name'})
        response = client.simulate_patch(
            '/users/{}'.format(doc['email']),
            body=data,
            headers={'content-type': 'application/json'}
        )
        assert response.status == falcon.HTTP_ACCEPTED


    def test_put_user(self, client):
        doc = self._make_user()
        response = client.simulate_put(
            '/users/{}'.format(doc['email']),
            body=json.dumps(FAKE_USER),
            headers={'content-type': 'application/json'}
        )
        assert response.status == falcon.HTTP_NO_CONTENT

class TestFiltering:

    def _load_data(self):
        data, errors = FilterSchema().post(json.dumps(
            {
                'value': 'value',
                'value1': 'value1',
                'value2': 'value2'
            }
        ))
        return data

    def test_roundtrip_list(self, client):
        doc = self._load_data()
        response = client.simulate_get('/filters')
        result_doc = json.loads(response.content.decode('utf-8'))
        assert 'value2' not in result_doc
        assert response.status == falcon.HTTP_OK

    def test_searching(self, client):
        schema = FilterSchema()
        schema.post(
            json.dumps({
                'value': 'schema1_value',
                'value1': 'schema1_value1',
                'value2': 'schema1_value2'
            }))

        schema.post(
            json.dumps({
                'value': 'schema2_value',
                'value1': 'schema2_value1',
                'value2': 'schema2_value2'
            }))

        # Pass the args as they would appear from ``get_filter``
        result = schema.find(**{'filter': {'value1': 'schema2_value1'}})
        assert result.count() == 1
        assert result[0]['value1'] == 'schema2_value1'

    def test_advanced_query(self, client):
        """Test a mongodb query operator
        """
        schema = FilterSchema()
        # Purposefully omitting some fields
        schema.post(
            json.dumps({
                'value': 'schema1_value',
                'value2': 'schema1_value2'
            }))

        schema.post(
            json.dumps({
                'value': 'schema2_value',
                'value1': 'schema2_value1',
            }))

        result = schema.find(**{"filter": {"value1": {"$exists": True}}})
        assert result.count() == 1
        assert result[0]['value1'] == 'schema2_value1'


class TestFileResource:

    def create_resource(self, client):
        # Create the file store and resource
        path = os.path.dirname(__file__)
        store = FileStore(path, namegen=lambda: '0xa6a6a6')
        resource = FileCollection(store)
        item_resource = FileItem(store)
        client.app.add_route(resource.uri_template, resource)
        client.app.add_route(item_resource.uri_template, item_resource)
        return store

    def test_posted_image_gets_saved(self, client):

        # Create the file store and resource
        store = self.create_resource(client)

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
        store = self.create_resource(client)
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
        store = self.create_resource(client)
        # create an image
        name = store._namegen()
        filename = "{}.png".format(name)
        path = os.path.join(store._storage_path, filename)
        with open(path, 'wb') as fobj:
            fobj.write(b'fake image')

        response = client.simulate_get(
            '/files/{}'.format(filename)
        )
        assert response.status == falcon.HTTP_OK
        os.unlink(path)

class TestSchema:

    def test_constraints(self):
        """Test the constraints specified on
        the schema were created
        """
        schema = UserSchema()
        coll = schema.get_collection()
        indexes = coll.index_information()
        for key, kwargs in schema.opts.constraints:
            index_key = "{}_1".format(key)
            assert index_key in indexes
            for item in kwargs:
                assert item in indexes[index_key]

    def test_db_name(self):
        schema = UserSchema()
        assert schema._db_name() == 'plume_userschema'

    def test_uniqueness(self):
        """Test we cannot make duplicate entries
        """
        schema = UserSchema()
        data = json.dumps(FAKE_USER)
        user, errors = schema.post(data)
        assert len(errors) == 0
        user_duplicate, errors = schema.post(data)
        assert 'duplicate_key' in errors

    def test_count(self):
        """Sanity check for the schema ``count`` method
        """
        schema = UserSchema()
        count = schema.count()
        db = get_database()
        assert count == db[schema._db_name()].count()
