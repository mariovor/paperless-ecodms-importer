import json
from datetime import datetime
from pathlib import Path
from time import sleep

import requests

from paperless import PaperlessDocument
from utils import MigrationLogger

SOURCE_SYSTEM_TAG = 'EcoDMS'

TAX_RELEVANT = 'Steuerrelevant'
EXECUTED_LOG = 'executed.json'

logger = MigrationLogger.get_logger()


class AttributeTypes:
    """
    Paperless document attributes which can be updated and retrieved from server
    """
    TAGS = 'tags'
    DOCUMENT_TYPES = 'document_types'


class PaperlessAPI:

    def __init__(self, token: str, api_url: str):
        self.authentication_header = {'Authorization': f'Token {token}'}
        self.api_url = api_url
        self.tags = self._retrieve_tags()
        self.document_types = self._retrieve_document_types()

    def _retrieve_tags(self) -> dict:
        """
        Retrieve tags from paperless server
        """
        return self._retrieve_attributes(AttributeTypes.TAGS)

    def _retrieve_document_types(self) -> dict:
        """
        Retrieve document types from paperless server
        """
        return self._retrieve_attributes(AttributeTypes.DOCUMENT_TYPES)

    def _retrieve_attributes(self, attribute_type: str) -> dict:
        """
        Update dict with content of attribute_type from paperless server
        """
        attributes_response = requests.get(f'{self.api_url}/{attribute_type}/', headers=self.authentication_header)
        attributes = {}
        for attribute in attributes_response.json()['results']:
            attributes[attribute['name']] = int(attribute['id'])
        logger.debug(f'Updating attribute with {attributes}')

        return attributes

    def add_tag(self, tag: str):
        """
        Add tag to server. Updates after successful action he internal dict of tags.
        :param tag: The tag name
        """
        self._add_attribute(AttributeTypes.TAGS, tag)
        self.tags = self._retrieve_tags()

    def add_document_types(self, document_type: str):
        """
        Add document type to server. Updates after successful action he internal dict of tags.
        :param document_type: The document type to be added.
        """
        self._add_attribute(AttributeTypes.DOCUMENT_TYPES, document_type)
        self.document_types = self._retrieve_document_types()

    def _add_attribute(self, attribute_type: str, attribute_value: str):
        """
        Adds a new attribute to the server.
        :param attribute_type: The element type to be added. Must be a valid paperless element, like 'tags'.
        :param attribute_value: The value of the element type to be added
        """
        data = {'name': attribute_value}
        response = requests.post(f'{self.api_url}/{attribute_type}/', headers=self.authentication_header,
                                 json=data)
        if response.status_code == 201:
            logger.info(f'Successfully added {attribute_value} to {attribute_type}')
        else:
            raise RuntimeError(
                f'Failed to add  {attribute_value} to {attribute_type} with code {response.status_code} / reason {response.reason}')

    def get_or_create_tag_id(self, tag: str) -> int:
        """
        Return the id of tag.
        If it does not exist, it will be created.
        :param tag: The tag name
        :return: The id of tag
        """
        if tag not in self.tags:
            self.add_tag(tag)
            return self.get_or_create_tag_id(tag)
        else:
            return self.tags[tag]

    def get_or_create_document_type_id(self, document_type: str) -> int:
        """
        Return the id of document_type.
        If it does not exist, it will be created.
        :param document_type: The document_type name
        :return: The id of tag
        """
        if document_type not in self.document_types:
            self.add_document_types(document_type)
            return self.get_or_create_document_type_id(document_type)
        else:
            return self.document_types[document_type]

    def upload_documents(self, documents: [PaperlessDocument]) -> None:
        """
        Upload alist of PaperlessDocuments to paperless.
        """
        for document in documents:
            self.upload_document(document)

    def upload_document(self, document: PaperlessDocument):
        """
        Upload a PaperlessDocument to paperless.
        """
        if not self.is_document_new(str(document.filepath)):
            logger.info(f"Skipping {document.filepath}! Has been already uploaded in the past")
            return None

        tags = [self.get_or_create_tag_id(document.folder), self.get_or_create_tag_id(SOURCE_SYSTEM_TAG)]
        document_types = [self.get_or_create_document_type_id(document.document_type)]

        # Special handling for workflow of original author
        if document.tax_relevant:
            tags.append(self.get_or_create_tag_id(TAX_RELEVANT))

        payload = self._preprare_payload(
            title=document.title,
            tags=tags,
            created=document.created,
            archive_serial_number=document.asn,
            document_type=document_types
        )
        logger.info(f'Uploading document "{document.title}"')
        response = self._upload(document.filepath, payload)
        self._wait_upload_done(response)
        self.write_executed(str(document.filepath))

    def _preprare_payload(self,
                          title=None,
                          created=None,
                          correspondent=None,
                          document_type=None,
                          storage_path=None,
                          tags=None,
                          archive_serial_number=None,
                          custom_fields=None
                          ) -> dict:
        """
        Generate the payload for the upload request.
        :param title: Optional title of the document.
        :param created: Optional creation date/time of the document.
        :param correspondent: Optional correspondent ID.
        :param document_type: Optional document type ID.
        :param storage_path: Optional storage path ID.
        :param tags: Optional list of tag IDs.
        :param archive_serial_number: Optional archive serial number.
        :param custom_fields: Optional list of custom field IDs.
        :return: A dict containing the payload for the request.
       """
        # Prepare the payload with optional metadata
        payload = {}
        if title:
            payload['title'] = title
        if created:
            payload['created'] = created
        if correspondent:
            payload['correspondent'] = correspondent
        if document_type:
            payload['document_type'] = document_type
        if storage_path:
            payload['storage_path'] = storage_path
        if archive_serial_number:
            payload['archive_serial_number'] = archive_serial_number
        if custom_fields:
            payload['custom_fields'] = custom_fields
        if tags:
            payload['tags'] = tags

        return payload

    def _upload(self, filepath: Path, payload: dict) -> str:
        """
        Read the file to be uploaded and create the request to Paperless to upload.
        """
        # Open the file and prepare the form data
        with open(filepath, 'rb') as document_file:
            files = {
                'document': document_file
            }

            # Send the POST request
            response = requests.post(f'{self.api_url}/documents/post_document/', headers=self.authentication_header,
                                     files=files, data=payload)

        # Check if the request was successful
        if response.status_code == 200:
            return response.json()  # Return the UUID of the consumption task
        else:
            return f"Failed to upload document. Status Code: {response.status_code}, Response: {response.text}"

    def _wait_upload_done(self, uuid: str) -> bool:
        success = None
        while not success:
            response = requests.get(f'{self.api_url}/tasks/?task_id={uuid}', headers=self.authentication_header)
            status = response.json()[0]['status']
            logger.info(f'Job {uuid} is in status {status}')
            if status == 'SUCCESS':
                success = True
                break
            elif status == 'FAILURE':
                success = False
                break
            else:
                sleep(10)
        return success

    def is_document_new(self, file_name: str) -> bool:
        """
        Check if file_name has been executed in the past
        :param file_name: The file name
        :return:
        """
        executed_log = self._read_executed_log_from_file_system()
        return file_name not in executed_log.keys()

    def _read_executed_log_from_file_system(self) -> dict:
        """
        Read the execution log from file system.
        Return empty one if file does not exist.
        :return:Execution log as dict
        """
        try:
            with open(EXECUTED_LOG, 'r') as f:
                executed_log = json.load(f)
        except FileNotFoundError:
            logger.info(f'Could not decode execution log under {EXECUTED_LOG}. Assuming is empty.')
            return {}
        return executed_log

    def _write_executed_log_to_file_system(self, log: dict):
        """
        Write a new execution log to file system.
        :param log: The content of the log
        """
        with open(EXECUTED_LOG, 'w') as f:
            json.dump(log, f)

    def write_executed(self, file_name: str):
        """
        Append the exeucution log with the entry.
        :param file_name: The used file name
        """
        executed_log = self._read_executed_log_from_file_system()
        executed_log[file_name] = datetime.now().isoformat()
        self._write_executed_log_to_file_system(executed_log)
