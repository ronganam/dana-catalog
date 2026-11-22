"""The catalog entries a pull request adds or changes, as JSON for a workflow matrix.

    python scripts/changed_entries.py <base ref>      (prints [{...entry...}, ...] on one line)

Compares catalog.json at <base ref> (git show) with the file in the working tree, by
entry name: a new name or an entry that differs is listed; removed entries are not (there
is nothing to check). Standard library only.
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List


def entries(data: Any) -> Dict[str, Dict[str, Any]]:
    """The entries of a catalog by name (entries without a string name are skipped: Dana's parser reports them)."""
    items = data.get("addons", []) if isinstance(data, dict) else []
    return {e["name"]: e for e in items if isinstance(e, dict) and isinstance(e.get("name"), str)}


def changed(base: Any, head: Any) -> List[Dict[str, Any]]:
    """The entries of ``head`` that are new or differ from ``base``'s."""
    before = entries(base)
    return [e for name, e in entries(head).items() if before.get(name) != e]


def main(ref: str) -> None:
    shown = subprocess.run(["git", "show", f"{ref}:catalog.json"], capture_output=True, text=True)
    base = json.loads(shown.stdout) if shown.returncode == 0 else {"addons": []}
    head = json.loads(Path("catalog.json").read_text(encoding="utf-8"))
    print(json.dumps(changed(base, head)))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: python scripts/changed_entries.py <base ref>")
    main(sys.argv[1])
