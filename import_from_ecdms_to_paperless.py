import os
import xml.etree.ElementTree as ET
from pathlib import Path

from ecodms import parse_documents, Document
from paperless import PaperlessDocument
from paperless_api import PaperlessAPI
from utils import MigrationLogger

logger = MigrationLogger.get_logger()

ECODMS_PATH_EXPORT_FILE = os.getenv("ECODMS_PATH_EXPORT_FILE")
PAPERLESS_API_URL = os.getenv("PAPERLESS_API_URL")
PAPERLESS_TOKEN = os.getenv("PAPERLESS_TOKEN")

def to_paperless(ecodms_documents: [Document]) -> [PaperlessDocument]:
    export_file_path = Path(ECODMS_PATH_EXPORT_FILE)
    export_archive_path = export_file_path.parent
    paperless_documents = []
    for ecodms_document in ecodms_documents:
        version = ecodms_document.classifyInfos[0].versions[0]
        paperless_documents.append(PaperlessDocument(
            filepath=export_archive_path.joinpath(ecodms_document.files[0].filePath),
            title=version.bemerkung,
            created=version.datum,
            folder=version.hauptordner,
            asn=int(float(version.laufende_nummer)) if version.laufende_nummer != 'null' else None,
            tax_relevant=True if version.steuerrelevant=='0' or version.steuerrelevant=='2' else False,
        ))

    return paperless_documents

if __name__ == "__main__":
    logger.info(f"Path to EcoDMS export file {ECODMS_PATH_EXPORT_FILE}")
    # Parse the XML file
    tree = ET.parse(ECODMS_PATH_EXPORT_FILE)
    root_element = tree.getroot()

    # Convert to dataclass
    documents_data = parse_documents(root_element)
    paperless_docs = to_paperless(documents_data.documents)

    # Upload
    api = PaperlessAPI(PAPERLESS_TOKEN, PAPERLESS_API_URL)
    api.upload_documents(paperless_docs)