from google.cloud import datastore
from .exceptions import QueryIsNoneException


class DataStoreUtil:
    """
    Auxiliary class for Google Cloud Scheduler
    TODO it needs to be improved
    """

    def __init__(self, kind):
        self._kind = kind
        self._client = datastore.Client()
        self._entity = None
        self._query = None

    @property
    def entity(self):
        if not self._entity:
            self._entity = datastore.Entity(key=self._client.key(self._kind))
        return self._entity

    def put(self, entry):
        # load the entity
        self.entity.update(entry)
        # save in datastore
        self._client.put(self.entity)
        return self.entity

    @property
    def query(self):
        if not self._query:
            self._query = self._client.query(kind=self._kind)
        return self._query

    def query_reset(self):
        self._query = None

    def delete_multi(self, query=None):
        if not query:
            raise QueryIsNoneException()

        keys = [self._client.key(self._kind, e.id) for e in query.fetch()]

        self._client.delete_multi(keys)
