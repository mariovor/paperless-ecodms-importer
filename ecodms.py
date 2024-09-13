from dataclasses import dataclass, field
from typing import Optional, List
from xml.etree import ElementTree as ET


@dataclass
class Version:
    ordner: Optional[str]
    hauptordner: Optional[str]
    bemerkung: Optional[str]
    status: Optional[str]
    revision: Optional[str]
    dokumentenart: Optional[str]
    letzte_aenderung: Optional[str]
    datum: Optional[str]
    bearbeitet_von: Optional[str]
    zurueckgestellt_bis: Optional[str]
    zu_bearbeiten: Optional[str]
    zur_ansicht: Optional[str]
    typ: Optional[str]
    laufende_nummer: Optional[str]
    steuerrelevant: Optional[str]
    ordner_extkey: Optional[str]


@dataclass
class ClassifyInfo:
    cla_docs_id: str
    revision_count: str
    trashed: bool
    versions: List[Version] = field(default_factory=list)


@dataclass
class File:
    id: str
    origname: str
    filePath: str


@dataclass
class Document:
    docid: str
    files: List[File] = field(default_factory=list)
    classifyInfos: List[ClassifyInfo] = field(default_factory=list)


@dataclass
class Documents:
    user: str
    startid: str
    endid: str
    documents: List[Document] = field(default_factory=list)


def parse_version(element: ET.Element) -> Version:
    return Version(
        ordner=element.findtext('ordner'),
        hauptordner=element.findtext('hauptordner'),
        bemerkung=element.findtext('bemerkung'),
        status=element.findtext('status'),
        revision=element.findtext('revision'),
        dokumentenart=element.findtext('dokumentenart'),
        letzte_aenderung=element.findtext('letzte-änderung'),
        datum=element.findtext('datum'),
        bearbeitet_von=element.findtext('bearbeitet-von'),
        zurueckgestellt_bis=element.findtext('zurückgestellt-bis'),
        zu_bearbeiten=element.findtext('zu-bearbeiten'),
        zur_ansicht=element.findtext('zur-ansicht'),
        typ=element.findtext('typ'),
        laufende_nummer=element.findtext('laufende-nummer'),
        steuerrelevant=element.findtext('steuerrelevant'),
        ordner_extkey=element.findtext('ordner-extkey')
    )


def parse_classify_info(element: ET.Element) -> ClassifyInfo:
    versions = [parse_version(ver) for ver in element.findall('Version')]
    return ClassifyInfo(
        cla_docs_id=element.attrib['cla_docs_id'],
        revision_count=element.attrib['revision_count'],
        trashed=element.attrib['trashed']=='true',
        versions=versions
    )


def parse_file(element: ET.Element) -> File:
    return File(
        id=element.attrib['id'],
        origname=element.attrib['origname'],
        filePath=element.attrib['filePath']
    )


def parse_document(element: ET.Element) -> Document:
    files = [parse_file(f) for f in element.findall('files')]
    classifyInfos = [parse_classify_info(ci) for ci in element.findall('classifyInfos/classifyInfo')]
    return Document(
        docid=element.attrib['docid'],
        files=files,
        classifyInfos=classifyInfos
    )


def parse_documents(root_element: ET.Element) -> Documents:
    documents = [parse_document(doc) for doc in root_element.findall('document')]
    return Documents(
        user=root_element.attrib['user'],
        startid=root_element.attrib['startid'],
        endid=root_element.attrib['endid'],
        documents=documents
    )
