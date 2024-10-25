from dataclasses import dataclass
from pathlib import Path


@dataclass
class PaperlessDocument:
    filepath: Path
    title: str = None
    created: str = None
    folder: str = None
    asn: int = None
    tax_relevant: bool = None