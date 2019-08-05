import logging

from google.cloud import storage
from google.api_core.exceptions import NotFound
from google.cloud.storage.bucket import Bucket
from .exceptions import NoBlobSetException
from .project import ProjectReference


class StorageUtil:
    """
    Auxiliary class for Google Cloud Storage

    Example:
        buckets = ''
        for bucket in Storage.buckets():
            buckets += f'{bucket}\n'

        project_def = ProjectDefinition('project_id', 'location')
        strge = StorageUtil('bucket-name', 'all_buckets.txt', project=project_def).new_content(buckets)
        print(f'File content [{strge.file_name}]: {strge.get_content()}')
    """

    client = storage.Client()

    def __init__(self, bucket_name, file_name=None, project=None, project_id=None, location=None):
        self.project = project if project else ProjectReference(project_id, location)
        self._bucket_name = bucket_name
        self._bucket = None
        self._blob = None
        self._file_name = file_name
        if file_name:
            self.set_blob(file_name)

    @property
    def bucket(self):
        if not self._bucket:
            try:
                self._bucket = self.client.get_bucket(self._bucket_name)
            except NotFound:
                self._bucket = Bucket(client=self.client, name=self._bucket_name)
                self._bucket.create(client=self.client, location=self.project.location)
                logging.info('Bucket {} not found and was created.'.format(self._bucket.name))

        return self._bucket

    @property
    def blob(self):
        if not self._blob:
            raise NoBlobSetException()
        return self._blob

    @property
    def file_name(self):
        if not self._blob:
            raise NoBlobSetException()
        return self._file_name

    def set_blob(self, file_name):
        self._file_name = file_name
        self._blob = self.bucket.get_blob(file_name)
        if not self._blob:
            self._blob = self._bucket.blob(file_name)
            logging.info(f'File not found and was created: {file_name}')
        return self

    def delete_blob(self):
        try:
            self.bucket.delete_blob(self.file_name)
            logging.info(f'File deleted: {self.file_name}')
        except NotFound:
            logging.info(f'File not found: {self.file_name}')

        self._file_name = None
        self._blob = None
        return self

    def new_content(self, new_content: str):
        content_len = 80
        content = f'{new_content[:content_len]} [...]' if len(new_content) > content_len else new_content
        logging.info(f'Uploading new content to file "{self._file_name}": {repr(content)}')
        self.blob.upload_from_string(new_content)
        return self

    def get_content(self):
        return self.blob.download_as_string()

    @classmethod
    def buckets(cls):
        return [b for b in cls.client.list_buckets()]
