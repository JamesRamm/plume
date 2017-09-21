"""Connect to MongoDB and provide a base schema which will
save deserialized data to a collection

The connections to mongodb are cached. Inspired by MongoEngine
"""
import simplejson
import pymongo
from bson.objectid import ObjectId
from marshmallow import Schema, fields, SchemaOpts, ValidationError
from feather.connection import get_database
from feather import errors

def _check_object_id(filter_spec):
    """Replaces the object id string in a filter spec with a pymongo
    ``ObjectId``
    """
    if '_id' in filter_spec:
        filter_spec['_id'] = ObjectId(filter_spec['_id'])


class MonogSchemaOpts(SchemaOpts):
    """Adds 'constraints' option
    """
    def __init__(self, meta, **kwargs):
        SchemaOpts.__init__(self, meta, **kwargs)
        self.constraints = getattr(meta, 'constraints', ())


class MongoSchema(Schema):
    """A Marshmallow schema backed by MongoDB

    When data is loaded (deserialized) it is saved to a mongodb
    document in a collection matching the Schema name (and containing app - similar to
    Django table names)

    This enables marshmallow to behave as an ORM to MongoDB
    """
    OPTIONS_CLASS = MonogSchemaOpts

    _id = fields.Str(dump_only=True)

    def __init__(self, *args, **kwargs):
        super(MongoSchema, self).__init__(*args, **kwargs)

        # Name for the table/collection in the database
        self._name = kwargs.get('name', None)

        # Create any constraints for this collection
        self._create_constraints(self.get_collection())

    def _db_name(self):
        """Generate a name for the backend representation of this schema.
        I.e the name for the mongodb collection, sql table or disk file
        """
        if not self._name:
            class_name = self.__class__.__name__
            # Get the name of the current package. The last entry will be the module name
            # which we dont want
            name_parts = __name__.split('.')[:-1]
            name_parts.append(class_name.lower())
            self._name = "_".join(name_parts)
        return self._name

    def _create_constraints(self, collection):
        for key, kwargs in self.opts.constraints:
            collection.create_index(key, **kwargs)

    def get_collection(self):
        """Return the collection associated with this schema
        """
        # We get the connected mongo database and generate a collection
        # name based on the name of this schema. Mongodb will create the
        # collection if it doesn't already exist
        name = self._db_name()
        collection = get_database()[name]
        return collection

    def find(self, *args, **kwargs):
        """Wraps pymongo's `find` for this collection
        """
        collection = self.get_collection()
        return collection.find(*args, **kwargs)

    def get(self, filter_spec, *args, **kwargs):
        """Wraps pymongo's `find_one` for this collection
        """
        collection = self.get_collection()
        _check_object_id(filter_spec)
        return collection.find_one(filter_spec, *args, **kwargs)

    def post(self, data):
        """Shortcut for 'loads' that follows HTTP naming conventions
        """
        validated = self.loads(data)
        # Retrieve the collection in which this document should be inserted
        collection = self.get_collection()

        # Insert document(s) into the collection
        try:
            if self.many:
                collection.insert_many(validated.data)
            else:
                collection.insert_one(validated.data)
        except pymongo.errors.DuplicateKeyError as error:
            validated.errors[errors.DUPLICATE_KEY] = error.details

        return validated


    def patch(self, filter_spec, data):
        """'Patch' (update) an existing document
        """
        validated = self.loads(data, partial=True)
        collection = self.get_collection()
        _check_object_id(filter_spec)
        try:
            collection.update_one(filter_spec, {"$set": validated.data})
        except pymongo.errors.DuplicateKeyError as error:
            validated.errors[errors.DUPLICATE_KEY] = error.details

        return validated

    def put(self, filter_spec, data):
        """'Put' (replace) an existing document
        """
        validated = self.loads(data)
        collection = self.get_collection()
        _check_object_id(filter_spec)
        try:
            collection.replace_one(filter_spec, validated.data)
        except pymongo.errors.DuplicateKeyError as error:
            validated.errors[errors.DUPLICATE_KEY] = error.details

        return validated

    def delete(self, filter_spec):
        """Delete an existing document
        """
        collection = self.get_collection()
        _check_object_id(filter_spec)
        collection.delete_one(filter_spec)

    def count(self):
        """Wraps pymongo's `count` for this collection
        """
        collection = self.get_collection()
        return collection.count()
