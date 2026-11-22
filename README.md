# Dana add-on catalog

The list of add-ons a [Dana](https://github.com/ronganam/dana) server offers on its
Add-ons page. Each Dana server reads [`catalog.json`](catalog.json) from this repository
(`https://raw.githubusercontent.com/ronganam/dana-catalog/main/catalog.json`, the
`DANA_CATALOG_URL` setting); nothing here runs on a server until a person installs an
add-on and agrees to what it touches.

## An entry

```json
{
 "name": "plants",
 "title": "Plants",
 "description": "One sentence: what it does for the person.",
 "icon": "sprout",
 "author": "your GitHub name",
 "homepage": "https://github.com/you/dana-addon-plants",
 "tags": ["home"],
 "min_dana": "10.0.0",
 "touches": {"hosts": ["api.plants.example"], "acts_outside": false, "stores_credentials": true, "reads": []},
 "source": {"repo": "https://github.com/you/dana-addon-plants", "path": "", "ref": "<full 40-character commit hash>"}
}
```

- `name` is the add-on's manifest name (lower case, letters, digits and `_`); one entry per name.
- `source.ref` is a full commit hash, never a branch or tag: an entry is exactly one version.
  `source.path` is the add-on's folder inside the repository (`""` for the top).
- `touches` is what that version declares (`Touches` in its `addon.py`); people see it
  before installing, and Dana refuses an install whose add-on declares more.
- `min_dana` is the oldest Dana version it works with; older servers do not offer it.

The fields and the manifest they come from are described in Dana's
[add-on reference](https://github.com/ronganam/dana/blob/master/server/docs/addon-reference.md).

## Adding or updating your add-on

From a Dana checkout, with the GitHub CLI (`gh`) signed in:

```bash
server/bin/dana addons publish path/to/your-addon --dry-run   # prints every command first
server/bin/dana addons publish path/to/your-addon
```

`publish` runs `addons check` and `addons test`, pushes your add-on to
`<you>/dana-addon-<name>`, tags `v<version>` with a release, and opens a pull request here
that adds or replaces your entry, pinned to the released commit. Editing `catalog.json` by
hand in a pull request works too: one entry per pull request, entries sorted by name, one
space of indent.

## What every pull request is checked for

The [`Check entries`](.github/workflows/check.yml) workflow checks out Dana at a pinned
commit (`DANA_REF`) and, for every entry the pull request adds or changes:

1. `catalog.json` parses the way Dana reads it (no skipped entries);
2. the add-on at `source.ref` passes `bin/dana addons check` (manifest, imports, migrations,
   documented tool parameters, hosts and environment values it uses are declared);
3. its name and `touches` match the entry;
4. its own tests pass with `bin/dana addons test` against Dana's harness.

A reviewer then reads the add-on itself: that it does what the description says, keeps
secrets in credentials, uses made-up people in its tests, and touches only what it
declares. Removing an entry needs no checks.

## Scripts

`scripts/changed_entries.py` (the entries a pull request adds or changes) and
`scripts/verify_entry.py` (an entry against the check's report) use the standard library
only; the workflow runs them.
