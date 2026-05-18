"""Data models for BMS map source definitions."""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Tuple, Any


@dataclass
class BMSField:
    """A single field in a BMS map defined by a DFHMDF macro."""
    name: Optional[str]
    pos: Tuple[int, int]
    length: int
    attrb: List[str] = field(default_factory=list)
    color: Optional[str] = None
    hilight: Optional[str] = None
    initial: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'pos': list(self.pos),
            'length': self.length,
            'attrb': self.attrb,
            'color': self.color,
            'hilight': self.hilight,
            'initial': self.initial
        }

    def to_dict_compact(self) -> Dict[str, Any]:
        """Return dict with null/empty values omitted."""
        d: Dict[str, Any] = {'pos': list(self.pos), 'length': self.length}
        if self.name is not None:
            d['name'] = self.name
        if self.attrb:
            d['attrb'] = self.attrb
        if self.color is not None:
            d['color'] = self.color
        if self.hilight is not None:
            d['hilight'] = self.hilight
        if self.initial is not None:
            d['initial'] = self.initial
        return d


@dataclass
class BMSMap:
    """A single map in a BMS mapset defined by a DFHMDI macro."""
    name: str
    size: Tuple[int, int]
    ctrl: Optional[str] = None
    fields: List[BMSField] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'size': list(self.size),
            'ctrl': self.ctrl,
            'fields': [f.to_dict() for f in self.fields]
        }

    def to_dict_compact(self) -> Dict[str, Any]:
        """Return dict with null values omitted."""
        d: Dict[str, Any] = {'name': self.name, 'size': list(self.size)}
        if self.ctrl is not None:
            d['ctrl'] = self.ctrl
        d['fields'] = [f.to_dict_compact() for f in self.fields]
        return d


@dataclass
class BMSMapset:
    """A BMS mapset defined by a DFHMSD macro."""
    name: str
    lang: Optional[str] = None
    mode: Optional[str] = None
    storage: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'lang': self.lang,
            'mode': self.mode,
            'storage': self.storage
        }

    def to_dict_compact(self) -> Dict[str, Any]:
        """Return dict with null values omitted."""
        d: Dict[str, Any] = {'name': self.name}
        if self.lang is not None:
            d['lang'] = self.lang
        if self.mode is not None:
            d['mode'] = self.mode
        if self.storage is not None:
            d['storage'] = self.storage
        return d


@dataclass
class BMSMapDefinition:
    """Complete BMS map definition containing a mapset and its maps."""
    mapset: BMSMapset
    maps: List[BMSMap] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'mapset': self.mapset.to_dict(),
            'maps': [m.to_dict() for m in self.maps]
        }

    def to_dict_compact(self) -> Dict[str, Any]:
        """Return dict with null values omitted from all nested objects."""
        return {
            'mapset': self.mapset.to_dict_compact(),
            'maps': [m.to_dict_compact() for m in self.maps]
        }
