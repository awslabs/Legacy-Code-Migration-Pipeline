"""Data model for COBOL copybook record layouts."""

from dataclasses import dataclass, field
from typing import Optional, List, Dict


@dataclass
class RecordField:
    """A single field in a COBOL record layout."""
    level: int
    name: str
    pic: Optional[str] = None
    usage: Optional[str] = None
    occurs: Optional[int] = None
    redefines: Optional[str] = None
    children: List['RecordField'] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            'level': self.level,
            'name': self.name,
            'pic': self.pic,
            'usage': self.usage,
            'occurs': self.occurs,
            'redefines': self.redefines,
            'children': [c.to_dict() for c in self.children]
        }
