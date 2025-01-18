from pathlib import Path
from time import sleep

import requests

from paperless import PaperlessDocument
from utils import MigrationLogger

TAX_RELEVANT = 'Steuerrelevant'

logger = MigrationLogger.get_logger()


class PaperlessAPI:

    def __init__(self, token: str, api_url: str):
        self.authentication_header = {'Authorization': f'Token {token}'}
        self.api_url = api_url
        self.tags = {}

        self._retrieve_tags()

    def _retrieve_tags(self):
        """
        Update internal dict of tags from paperless server
        """
        tags_response = requests.get(f'{self.api_url}/tags/', headers=self.authentication_header)
        tags = {}
        for tag in tags_response.json()['results']:
            tags[tag['name']] = int(tag['id'])
        logger.debug(f'Updating tags with {tags}')
        self.tags = tags

    def add_tag(self, tag: str):
        """
        Adds a new tag to the server. Updates after successful action he internal dict of tags.
        :param tag: The tag name
        """
        data = {'name': tag}
        response = requests.post(f'{self.api_url}/tags/', headers=self.authentication_header,
                                 json=data)
        if response.status_code == 201:
            self._retrieve_tags()
            logger.info(f'Successfully added tag {tag}')
        else:
            raise RuntimeError(f'Failed to add tag {tag} with code {response.status_code} / reason {response.reason}')

    def get_or_create_tag_id(self, tag: str) -> int:
        """
        Return the id of tag.
        If it does not exist, it will be created.
        :param tag: The tag name
        :return: The id of tag
        """
        if tag not in self.tags:
            self.add_tag(tag)
            self.get_or_create_tag_id(tag)
        else:
            return  self.tags[tag]


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
        tags = [self.get_or_create_tag_id(document.folder)]
        if document.tax_relevant:
            tags.append(self.get_or_create_tag_id(TAX_RELEVANT))

        payload = self._preprare_payload(
            title=document.title,
            tags=tags,
            created=document.created,
            archive_serial_number=document.asn
        )
        logger.info(f'Uploading document "{document.title}"')
        response = self._upload(document.filepath, payload)
        self._wait_upload_done(response)

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

