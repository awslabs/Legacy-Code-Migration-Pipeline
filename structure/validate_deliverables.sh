#!/bin/bash
# Deliverable Validation Script
# Usage: ./validate_deliverables.sh [--quiet]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

python3 "$SCRIPT_DIR/acm/deliverable_validator.py" --project-path "$SCRIPT_DIR" "$@"