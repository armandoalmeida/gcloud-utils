import os
import json
import logging

from typing import Dict, List
from google.cloud import bigquery
from gcputils import BigQueryUtil, ProjectReference
from google.cloud.bigquery.dataset import DatasetReference
from google.cloud.bigquery.table import TableReference
from google.cloud.bigquery.schema import SchemaField


class SchemaReference:
    def __init__(self, dataset, table, schema):
        self.dataset: DatasetReference = dataset
        self.table: TableReference = table
        self.schema: List[SchemaField] = schema


class SchemaLoader:
    VALID_FIELD_TYPES = ['STRING', 'BYTES', 'INTEGER', 'INT64', 'FLOAT', 'FLOAT64', 'BOOLEAN', 'BOOL',
                         'TIMESTAMP', 'DATE', 'TIME', 'DATETIME', 'RECORD', 'STRUCT']

    def __init__(self, schemas_directory, project=None, project_id=None, location=None):
        self.project = project if project else ProjectReference(project_id, location)
        self._schemas_directory = schemas_directory
        self._json_schemas = None
        self._schemas = None

    @property
    def json_schemas(self) -> list:
        if self._json_schemas is None:
            self._load_directory()
        return self._json_schemas

    def _load_directory(self):
        self._json_schemas = []
        for f in os.listdir(self._schemas_directory):
            file_name, file_extension = os.path.splitext(f)
            if file_extension == '.json' and file_name != '__init__':
                with open(f'{self._schemas_directory}/{f}') as json_file:
                    data = json.load(json_file)
                    if 'schema' in data:
                        schema = data['schema']
                        schema['tableReference'] = data['tableReference']
                        self._json_schemas.append(schema)

                    logging.info(f'The file "{self._schemas_directory}/{f}" was successfully loaded')

    @property
    def schemas(self) -> Dict[str, SchemaReference]:
        if not self._schemas:
            self.load_schemas()
        return self._schemas

    def load_schemas(self) -> Dict[str, SchemaReference]:
        if not self._schemas:
            self._schemas = {}
            for schema in self.json_schemas:
                dataset_id = schema['tableReference']['datasetId']
                table_id = schema['tableReference']['tableId']
                reference = f'{dataset_id}.{table_id}'

                bq_schema = self.get_bigquery_schema(schema)

                # check if the definition is the same of the bigquery existing table
                # if the table doesnt exist, it creates one
                bq_util = BigQueryUtil(dataset_id, table_id, schema=bq_schema, project_id=self.project.project_id,
                                       location=self.project.location)
                bq_util.check_table()

                # generate the schema reference
                schema_ref = SchemaReference(bq_util.dataset, bq_util.table, bq_util.schema)

                self._schemas[reference] = schema_ref
                logging.info(f"Schema loaded: {schema_ref.table.path}")

        return self._schemas

    @staticmethod
    def get_bigquery_schema(schema) -> list:
        fields = []
        if 'fields' in schema:
            for field in schema['fields']:
                if 'name' not in field or 'type' not in field:
                    raise Exception('Fields name and type are required')

                field_name = str(field['name']).strip()
                field_type = str(field['type']).strip()  # validate types

                if field_type not in SchemaLoader.VALID_FIELD_TYPES:
                    raise Exception(f'Invalid type: {field_type}')

                field_description = field['description'] if 'description' in field else None
                field_fields = ()
                if field_type == 'RECORD' or field_type == 'STRUCT':
                    if 'fields' not in field:
                        raise Exception('Fields property is required when the type is RECORD or STRUCT')
                    field_fields = tuple(SchemaLoader.get_bigquery_schema({'fields': field['fields']}))

                field_mode = "NULLABLE" if 'mode' not in field else str(field['mode']).strip()
                bq_field = bigquery.SchemaField(field_name, field_type, description=field_description,
                                                mode=field_mode, fields=field_fields)
                fields.append(bq_field)
        return fields
