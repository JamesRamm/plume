"""Connect to MongoDB and provide a base schema which will
save deserialized data to a collection

The connections to mongodb are cached. Inspired by MongoEngine
"""
from pymongo import MongoClient

DEFAULT_CONNECTION_NAME = 'default'
_connections = {}
_databases = {}

def connect(database='default', alias=DEFAULT_CONNECTION_NAME, **kwargs):
    """Connect to a database or retrieve an existing connection"""
    try:
        client = _connections[alias]
    except KeyError:
        client = MongoClient(**kwargs)
        _connections[alias] = client

    _databases[alias] = client[database]
    return client

def disconnect(alias=DEFAULT_CONNECTION_NAME):
    """Close the connection with a given alias."""
    if alias in _connections:
        _connections[alias].close()
        del _connections[alias]

def get_database(alias=DEFAULT_CONNECTION_NAME):
    """Get an existing database"""
    return _databases[alias]
