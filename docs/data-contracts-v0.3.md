# V0.3 — Data Correctness contracts

## Goal

Input validation and safe output publication come before performance or new CLI commands.
Data commands now fail explicitly on ambiguous or corrupt inputs.

| Operation | Validation | Output policy |
|---|---|---|
| CSV merge | Exact ordered headers, nonempty unique column names, equal row widths | Stream into temp file; atomically replace destination only on success |
| CSV split | Positive rows-per-file, valid header and rows | Stage all parts; **refuse** to overwrite any existing `part_NNN.csv` |
| CSV → JSON | Strict CSV header/row checks | Streaming JSON array; atomic publication |
| JSON → CSV | Top-level array of objects; consistent field set; duplicate key rejection | Incremental array parsing; atomic publication |
| JSONL merge | Each nonblank line must be valid JSON | Stream and validate; atomic publication |
| Excel → CSV | Sheet must exist; workbook closes even on errors | Read-only row iterator; atomic publication |
| JSON flatten/query | Escape literal separators and backslashes; reject ambiguous unflatten paths | Return mapping in memory; CLI output atomically written |

### Example: lossless paths

Input:

~~~json
{"a": {"b": 1}, "a.b": 2}
~~~

The flat result contains two different keys: `a.b` (nested path) and
`a\.b` (literal dot in a key). This preserves round trips through
`unflatten_json`. Escape a literal backslash as `\\`.

### Compatibility and limits

- Existing CLI command names and input flags remain unchanged.
- Data conversion intentionally **rejects** malformed rows or schemas formerly accepted silently.
- Existing single-file output destinations are replaced *after* a successful conversion. Output paths cannot alias inputs or be symlinks.
- Split chunk outputs never overwrite pre-existing part files.
- Individual JSON array objects may be buffered (up to 32 MiB per element); the entire array is not loaded.
- CSV cannot encode Python/JSON types without ambiguity: CSV → JSON yields **string values**; nested JSON values in JSON → CSV are encoded as JSON strings.
- Excel values are exported as read by `openpyxl`; formulas are not calculated. Sheet styling is not preserved.
- Atomic rename protects a single output on the same filesystem. Multi-file publication, unexpected power loss, or concurrent external writers are **not** fully transactional.
- CSV formula injection is a separate consumption risk when opening untrusted output in spreadsheet apps. This release preserves raw cell contents; no formula escaping is performed.
- The default CSV reader's field-size limits still apply; extremely large individual CSV fields may require future explicit limits.
