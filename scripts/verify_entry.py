"""Check one catalog entry against what `bin/dana addons check --json` says of the add-on at its commit.

    ENTRY='<the entry as JSON>' python scripts/verify_entry.py <check.json>

Fails (exit 1, a line per problem) when the check failed, the add-on declares another name,
or the entry's touches differ from what the add-on declares (people agree to the entry's
touches before installing; Dana refuses an install that touches more). Standard library only.
"""

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List

FIELDS = {"hosts": [], "acts_outside": False, "stores_credentials": False, "reads": []}


def touches(value: Any) -> Dict[str, Any]:
    """Touches with every field filled in (missing: the default), lists sorted."""
    value = value if isinstance(value, dict) else {}
    out = {k: value.get(k, default) for k, default in FIELDS.items()}
    return {k: sorted(v) if isinstance(v, list) else v for k, v in out.items()}


def problems(entry: Dict[str, Any], report: Dict[str, Any]) -> List[str]:
    """What is wrong with ``entry`` given the check's ``report``; [] when it is fine."""
    out: List[str] = []
    if not report.get("ok"):
        out += [f"check: {p['level']} {p.get('file', '')}: {p['message']} (fix: {p['fix']})"
                for p in report.get("problems", []) if p.get("level") == "error"]
    if report.get("name") != entry.get("name"):
        out.append(f"the add-on at that commit is {report.get('name')!r}, the entry says {entry.get('name')!r}")
    if entry.get("touches") is not None and touches(entry["touches"]) != touches(report.get("touches")):
        out.append(f"touches: the entry says {json.dumps(touches(entry['touches']))}, the add-on declares "
                   f"{json.dumps(touches(report.get('touches')))}: copy the add-on's")
    return out


def main(check_file: str) -> int:
    entry = json.loads(os.environ["ENTRY"])
    report = json.loads(Path(check_file).read_text(encoding="utf-8"))
    found = problems(entry, report)
    for line in found:
        print(f"::error title={entry.get('name')}::{line}")
    print(f"{entry.get('name')}: {'OK' if not found else f'{len(found)} problem(s)'}")
    return 1 if found else 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: ENTRY='{...}' python scripts/verify_entry.py <check.json>")
    sys.exit(main(sys.argv[1]))
