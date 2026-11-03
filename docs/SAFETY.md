# File safety and installation notes

## Destructive operations

- Use dry-run (the default) before adding `--execute`.
- `files dedup` only considers numbered copies such as `report (1).pdf`; their content must match the original byte-for-byte by SHA-256. This is not a general content-addressed duplicate scanner.
- `files rename` preflights all destinations, rejects collisions and path escapes, and stages files before completing the changes. It attempts rollback on ordinary exceptions, but is not an atomic filesystem transaction: interruptions, permissions, concurrent writers and platform differences can prevent full rollback.
- For important directories, back up your files first and avoid concurrent modification.

## Published package name conflict

The `devkit-tools` name on public PyPI belongs to an unrelated project (published from `yukinpost/devkit-cli`). The repository has not established a PyPI release under its own unique distribution name. To install this source project:

~~~bash
git clone https://github.com/1998x-stack/USEFULL_TOOLS.git
cd USEFULL_TOOLS
python -m pip install -e ".[all]"
~~~

The Python package import path and command name remain `devkit`. Choose a separate, available distribution name before publishing to PyPI.

## Conversion safety and quality reports

- The converter validates a staged single output before publishing it; failures before publication leave existing destinations untouched.
- A requested JSON quality report is published as a **separate** file. A valid document may already have been saved if the later report write fails: document + report are not a single atomic multi-file transaction.
- `fast` retains mandatory converter checks; `standard` adds independent content/structure evidence. `strict` PDF only supports matching approved visual fixtures in a locked environment.
- Markdown images must be local, exist and stay within the source document directory; remote image references are rejected before rendering.
- The six reviewed visual PNGs validate regression fixtures, not arbitrary customer documents or cross-platform PDF/A/accessibility features.
- More information: [Quality profiles](conversion-v0.4e.md), [Visual goldens](conversion-v0.4d.md), and [Troubleshooting](TROUBLESHOOTING.md).
