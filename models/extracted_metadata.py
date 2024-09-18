from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ExtractedMetadata:
    title: Optional[str]
    created_date: Optional[str]
    correspondent: Optional[str]
    document_type: Optional[str]
    tags: List[str]
