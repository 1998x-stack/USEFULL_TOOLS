# File safety and installation notes

## Destructive operations

- Use dry-run (the default) before adding \`--execute\`.
- \`files dedup\` only considers numbered copies such as \`report (1).pdf\`; their content must match the original byte-for-byte by SHA-256. This is not a general content-addressed duplicate scanner.
- \`files rename\` preflights all destinations, rejects collisions and path escapes, and stages files before completing the changes. It attempts rollback on ordinary exceptions, but is not an atomic filesystem transaction: interruptions, permissions, concurrent writers and platform differences can prevent full rollback.
- For important directories, back up your files first and avoid concurrent modification.

## Published package name conflict

The \`devkit-tools\` name on public PyPI belongs to an unrelated project (published from \`yukinpost/devkit-cli\`). The repository has not established a PyPI release under its own unique distribution name. To install this source project:

~~~bash
git clone https://github.com/1998x-stack/USEFULL_TOOLS.git
cd USEFULL_TOOLS
python -m pip install -e ".[all]"
~~~

The Python package import path and command name remain \`devkit\`. Choose a separate, available distribution name before publishing to PyPI.
