from dataclasses import dataclass
from pathlib import Path


@dataclass
class PaperlessDocument:
    filepath: Path
    title: str = None