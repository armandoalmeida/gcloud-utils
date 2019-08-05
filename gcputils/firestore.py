import logging
from google.cloud import firestore


class FireStoreUtil:
    """
    Auxiliary class for Google Cloud Scheduler

    Example:
    - Save a document:
        FireStoreUtil('coll', 'doc_id').set({...})
    - Select a document:
        FireStoreUtil('coll', 'doc_id').get()
    - Query:
        coll = FireStoreUtil('coll').collection
        docs = coll.where(u'field', u'==', u'value').limit(1).stream()
    """

    def __init__(self, collection_name, document_name=None):
        self._collection_name = collection_name
        self._document_name = document_name
        self._client = firestore.Client()
        self._collection = None
        self._document = None

    @property
    def collection(self):
        if not self._collection:
            self._document = self._client.collection(self._collection_name)
        return self._document

    @property
    def document(self, document_name=None):
        # forces new document
        if document_name is not None:
            self._document = self.collection.document(document_name)
        # creates a new document if it doesnt exist
        if not self._document:
            self._document = self.collection.document(self._document_name)
        return self._document

    def get(self):
        return self.document.get()

    def set(self, document):
        return self.document.set(document)

    def set_document_name(self, document_name):
        self._document_name = document_name

    def get_documents(self):
        return self.collection.stream()

    @staticmethod
    def delete_multi(docs):
        for doc in docs:
            logging.debug(u'Deleting doc {} => {}'.format(doc.id, doc.to_dict()))
            doc.reference.delete()

    def delete_collection(self, batch_size=10):
        docs = self.collection.limit(batch_size).stream()
        deleted = 0

        for doc in docs:
            logging.debug(u'Deleting doc {} => {}'.format(doc.id, doc.to_dict()))
            doc.reference.delete()
            deleted = deleted + 1

        if deleted >= batch_size:
            return self.delete_collection(batch_size)
