import os
import xml.etree.ElementTree as ET

from ecodms import parse_documents

PATH_ECODMS_EXPORT_FILE = os.getenv("PATH_ECODMS_EXPORT_FILE")

if __name__ == "__main__":
    print(f"Path to EcoDMS export file {PATH_ECODMS_EXPORT_FILE}")
    # Parse the XML file
    tree = ET.parse(PATH_ECODMS_EXPORT_FILE)
    root_element = tree.getroot()

    # Convert to dataclass
    documents_data = parse_documents(root_element)
    print(documents_data)
    i = 42
