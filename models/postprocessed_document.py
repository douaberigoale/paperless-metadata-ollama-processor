from dataclasses import dataclass
from typing import Optional, List


@dataclass
class PostProcessedDocument:
    title: str
    created: Optional[str]
    correspondent: Optional[int]
    document_type: Optional[int]
    tags: List[int]