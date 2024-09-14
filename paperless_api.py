from pathlib import Path

import requests

from paperless import PaperlessDocument

from logging import getLogger

LOGGER = getLogger(__name__)


class PaperlessAPI:

    def __init__(self, token: str, api_url: str):
        self.authentication_header = {'Authorization': f'Token {token}'}
        self.api_url = api_url

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
        payload = self._preprare_payload()
        response = self._upload(document.filepath, payload)
        LOGGER.info(f'Response is: {response}')

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
            # Add each tag as a separate entry
            for tag in tags:
                payload['tags'] = tag

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
            response = requests.post(f'{self.api_url}/documents/post_document/', headers=self.authentication_header, files=files, data=payload)

        # Check if the request was successful
        if response.status_code == 200:
            return response.json()  # Return the UUID of the consumption task
        else:
            return f"Failed to upload document. Status Code: {response.status_code}, Response: {response.text}"