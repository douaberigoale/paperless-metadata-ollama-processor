from dataclasses import dataclass
from typing import Optional, List


@dataclass
class Document:
    id: int
    title: str
    text: str
    created_date: Optional[str]
    correspondent_id: Optional[int]
    document_type_id: Optional[int]
    tag_ids: List[int]