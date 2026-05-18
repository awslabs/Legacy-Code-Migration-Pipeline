"""Parser for BMS map source files (.bms).

Parses DFHMSD, DFHMDI, and DFHMDF macros from BMS assembler source
into structured screen definitions.
"""

import re
import logging
from typing import Optional, List, Tuple

from tools.legacy_analyzer.models.bms_map import (
    BMSField,
    BMSMap,
    BMSMapset,
    BMSMapDefinition,
)

logger = logging.getLogger(__name__)


class BMSMapParser:
    """Parses BMS map source files (.bms) into structured screen definitions."""

    def parse(self, content: str) -> Tuple[BMSMapDefinition, Optional[str]]:
        """Parse BMS source content.

        Args:
            content: Raw BMS source file content.

        Returns:
            Tuple of (BMSMapDefinition, error_note).
            On success error_note is None.
            On failure returns an empty definition with an error description.
        """
        empty_def = BMSMapDefinition(mapset=BMSMapset(name=""))

        if not content or not content.strip():
            return empty_def, "Empty content"

        # Quick check: must contain at least one BMS macro
        if not any(macro in content.upper() for macro in ("DFHMSD", "DFHMDI", "DFHMDF")):
            return empty_def, "No BMS macros found in content"

        try:
            logical_lines = self._join_continuation_lines(content)
            return self._parse_logical_lines(logical_lines)
        except Exception as e:
            logger.warning("Failed to parse BMS content: %s", e)
            return empty_def, f"Parse error: {e}"

    def _join_continuation_lines(self, content: str) -> List[str]:
        """Join BMS continuation lines into logical lines.

        In BMS assembler format, a hyphen at column 72 (0-indexed position 71)
        indicates the line continues on the next line.
        """
        raw_lines = content.splitlines()
        logical_lines: List[str] = []
        i = 0

        while i < len(raw_lines):
            line = raw_lines[i]

            # Skip comment lines
            if line.startswith("*"):
                i += 1
                continue

            # Check for continuation: hyphen at position 71 (column 72)
            if len(line) >= 72 and line[71] == "-":
                # Start accumulating a continued logical line
                # Take content up to column 71 (positions 0-70)
                accumulated = line[:71].rstrip()
                i += 1

                # Keep joining while continuation lines follow
                while i < len(raw_lines):
                    next_line = raw_lines[i]
                    # Skip comment lines within continuations
                    if next_line.startswith("*"):
                        i += 1
                        continue

                    # Strip leading whitespace from continuation line
                    continuation_content = next_line.lstrip()

                    # Check if this continuation line itself continues
                    if len(next_line) >= 72 and next_line[71] == "-":
                        # Take content up to column 71
                        continuation_content = next_line[:71].lstrip().rstrip()
                        accumulated = accumulated + continuation_content
                        i += 1
                    else:
                        # Final line of this logical statement
                        accumulated = accumulated + continuation_content
                        i += 1
                        break

                logical_lines.append(accumulated)
            else:
                logical_lines.append(line)
                i += 1

        return logical_lines

    def _parse_logical_lines(
        self, lines: List[str]
    ) -> Tuple[BMSMapDefinition, Optional[str]]:
        """Parse logical lines for DFHMSD, DFHMDI, DFHMDF macros."""
        mapset = BMSMapset(name="")
        maps: List[BMSMap] = []
        current_map: Optional[BMSMap] = None

        for line in lines:
            upper_line = line.upper()

            # Skip empty lines
            if not line.strip():
                continue

            # Skip assembler TITLE directive (but not fields named TITLExx)
            stripped = line.lstrip()
            if stripped.upper().startswith("TITLE") and "DFHM" not in upper_line:
                continue

            # Skip END marker
            if upper_line.strip() == "END":
                continue

            if "DFHMSD" in upper_line:
                if "TYPE=FINAL" in upper_line:
                    continue
                mapset = self._parse_dfhmsd(line)
            elif "DFHMDI" in upper_line:
                current_map = self._parse_dfhmdi(line)
                maps.append(current_map)
            elif "DFHMDF" in upper_line:
                if current_map is not None:
                    field = self._parse_dfhmdf(line)
                    if field is not None:
                        current_map.fields.append(field)

        definition = BMSMapDefinition(mapset=mapset, maps=maps)
        return definition, None

    def _parse_dfhmsd(self, line: str) -> BMSMapset:
        """Parse a DFHMSD macro line to extract mapset info."""
        label = self._extract_label(line)
        params = self._extract_params(line)

        return BMSMapset(
            name=label or "",
            lang=params.get("LANG"),
            mode=params.get("MODE"),
            storage=params.get("STORAGE"),
        )

    def _parse_dfhmdi(self, line: str) -> BMSMap:
        """Parse a DFHMDI macro line to extract map info."""
        label = self._extract_label(line)
        params = self._extract_params(line)

        size = (24, 80)  # default
        size_val = params.get("SIZE")
        if size_val:
            size = self._parse_tuple(size_val)

        ctrl = None
        ctrl_val = params.get("CTRL")
        if ctrl_val:
            # CTRL can be (FREEKB) or FREEKB — strip parens
            ctrl = ctrl_val.strip("()")

        return BMSMap(name=label or "", size=size, ctrl=ctrl)

    def _parse_dfhmdf(self, line: str) -> Optional[BMSField]:
        """Parse a DFHMDF macro line to extract field info."""
        label = self._extract_label(line)
        params = self._extract_params(line)

        # POS is required for a valid field
        pos_val = params.get("POS")
        if not pos_val:
            return None

        pos = self._parse_tuple(pos_val)

        length = 0
        length_val = params.get("LENGTH")
        if length_val:
            try:
                length = int(length_val)
            except ValueError:
                length = 0

        attrb: List[str] = []
        attrb_val = params.get("ATTRB")
        if attrb_val:
            attrb = self._parse_list(attrb_val)

        color = params.get("COLOR")
        hilight = params.get("HILIGHT")

        initial = params.get("INITIAL")
        # INITIAL values may be quoted — strip quotes
        if initial and len(initial) >= 2:
            if (initial[0] == "'" and initial[-1] == "'"):
                initial = initial[1:-1]

        return BMSField(
            name=label if label else None,
            pos=pos,
            length=length,
            attrb=attrb,
            color=color,
            hilight=hilight,
            initial=initial,
        )

    def _extract_label(self, line: str) -> Optional[str]:
        """Extract the label from the first 8 columns of a BMS line.

        In assembler format, the label starts in column 1. If column 1 is a
        space, there is no label.
        """
        if not line or line[0] == " ":
            return None
        # Label is the first whitespace-delimited token
        parts = line.split()
        if parts:
            label = parts[0].strip()
            # Don't return macro names as labels
            if label.upper() in ("DFHMSD", "DFHMDI", "DFHMDF"):
                return None
            return label
        return None

    def _extract_params(self, line: str) -> dict:
        """Extract KEY=VALUE parameters from a BMS macro line.

        Handles:
        - Simple: KEY=VALUE
        - Parenthesized: KEY=(VAL1,VAL2)
        - Quoted: KEY='some text'
        - Ampersand values: KEY=&&SYSPARM
        """
        params = {}

        # Find the start of parameters (after the macro name)
        # Pattern: optional_label DFHMXX params
        macro_match = re.search(r"DFHM[A-Z]{2}\s+", line, re.IGNORECASE)
        if not macro_match:
            return params

        param_str = line[macro_match.end():]

        # Parse parameters using a state machine approach
        i = 0
        while i < len(param_str):
            # Skip whitespace and commas
            while i < len(param_str) and param_str[i] in (" ", ","):
                i += 1

            if i >= len(param_str):
                break

            # Find KEY=
            eq_pos = param_str.find("=", i)
            if eq_pos == -1:
                break

            key = param_str[i:eq_pos].strip().upper()
            i = eq_pos + 1

            if i >= len(param_str):
                params[key] = ""
                break

            # Parse value
            if param_str[i] == "(":
                # Parenthesized value — find matching close paren
                depth = 1
                start = i
                i += 1
                while i < len(param_str) and depth > 0:
                    if param_str[i] == "(":
                        depth += 1
                    elif param_str[i] == ")":
                        depth -= 1
                    i += 1
                value = param_str[start:i]
                params[key] = value
            elif param_str[i] == "'":
                # Quoted value — find matching close quote
                # Handle doubled quotes inside (e.g., 'it''s')
                start = i
                i += 1
                while i < len(param_str):
                    if param_str[i] == "'":
                        # Check for doubled quote
                        if i + 1 < len(param_str) and param_str[i + 1] == "'":
                            i += 2
                            continue
                        else:
                            i += 1
                            break
                    i += 1
                value = param_str[start:i]
                params[key] = value
            else:
                # Simple value — read until comma or space
                start = i
                while i < len(param_str) and param_str[i] not in (",", " "):
                    i += 1
                value = param_str[start:i].strip()
                params[key] = value

        return params

    def _parse_tuple(self, value: str) -> Tuple[int, int]:
        """Parse a parenthesized tuple like (24,80) into (int, int)."""
        cleaned = value.strip("()")
        parts = cleaned.split(",")
        if len(parts) == 2:
            try:
                return (int(parts[0].strip()), int(parts[1].strip()))
            except ValueError:
                pass
        return (0, 0)

    def _parse_list(self, value: str) -> List[str]:
        """Parse a parenthesized list like (ASKIP,NORM) into ['ASKIP', 'NORM']."""
        cleaned = value.strip("()")
        if not cleaned:
            return []
        return [item.strip() for item in cleaned.split(",") if item.strip()]
