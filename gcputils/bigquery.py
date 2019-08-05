import logging

from google.cloud import bigquery
from google.api_core.exceptions import NotFound
from .exceptions import SchemaNotDefinedException, BigQueryCheckingException, DifferentTableSchemaException
from .project import ProjectReference


class BigQueryUtil:
    client = bigquery.Client()

    def __init__(self, dataset_id, table_name, schema=None, project=None, project_id=None, location=None):
        self.project = project if project else ProjectReference(project_id, location)
        self.dataset_id = dataset_id
        self.table_name = table_name
        self._schema = schema
        self._dataset = None
        self._table = None

    @property
    def dataset(self) -> bigquery.dataset.DatasetReference:
        if not self._dataset:
            try:
                self._dataset = self.client.get_dataset(self.dataset_id)
            except NotFound:
                self._dataset = bigquery.Dataset(self.client.dataset(self.dataset_id))
                self._dataset.location = self.project.location
                self._dataset = self.client.create_dataset(self._dataset)
                logging.info(f'Created dataset {self._dataset.project}.{self.dataset_id}')
        return self._dataset

    @property
    def table(self) -> bigquery.table.TableReference:
        if not self._table:
            table_id = f'{self.project.project_id}.{self.dataset.dataset_id}.{self.table_name}'
            try:
                self._table = self.client.get_table(table_id)
            except NotFound:
                if not self.schema:
                    raise SchemaNotDefinedException()

                self._table = bigquery.Table(table_id, schema=self.schema)
                self._table = self.client.create_table(self._table)
                logging.info(f'Created table {self._table.project}.{self._table.dataset_id}.{self._table.table_id}')

        return self._table

    @property
    def schema(self):
        if not self._schema and self.table:
            # noinspection PyUnresolvedReferences
            return self.table.schema
        return self._schema

    @schema.setter
    def schema(self, schema):
        self._schema = schema
        self._table = None

    def check_table(self):
        if self.table is None:
            raise BigQueryCheckingException()

        # noinspection PyUnresolvedReferences
        if self.schema != self.table.schema:
            raise DifferentTableSchemaException()

        return self

    def import_data_from_json_file(self, file_uri):
        client = bigquery.Client()

        job_config = bigquery.LoadJobConfig()
        job_config.autodetect = False
        job_config.schema = self.schema
        job_config.source_format = bigquery.SourceFormat.NEWLINE_DELIMITED_JSON
        job_config.location = self.project.location

        load_job = client.load_table_from_uri(
            file_uri,
            self.dataset.table(self.table.table_id),
            location=self.project.location,
            project=self.project.project_id,
            job_config=job_config,
        )

        logging.info(f"Starting job {load_job.job_id}")
        load_job.result()  # Waits for table load to complete.
        logging.info(f"Job finished {load_job.job_id}")
