"""Pandoc JSON AST to typed DocumentIR projection.

The original AST is retained as serialized JSON so rendering never relies on a
lossy re-creation of Pandoc nodes from a simplified structural projection.
"""

import json
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple


@dataclass(frozen=True)
class InlineNode:
    kind: str
    text: str = ""
    target: Optional[str] = None
    children: Tuple["InlineNode", ...] = ()


@dataclass(frozen=True)
class BlockNode:
    kind: str
    source_ref: str
    inlines: Tuple[InlineNode, ...] = ()
    children: Tuple["BlockNode", ...] = ()
    level: int = 0
    text: str = ""
    row_span: int = 1
    col_span: int = 1


@dataclass(frozen=True)
class DocumentIR:
    """Immutable structural projection with the full original Pandoc AST."""

    blocks: Tuple[BlockNode, ...]
    ast_json: str
    features: Tuple[Tuple[str, int], ...]
    image_sources: Tuple[str, ...]

    def to_pandoc_ast(self) -> Dict[str, Any]:
        return json.loads(self.ast_json)

    def feature_count(self, kind: str) -> int:
        return dict(self.features).get(kind, 0)


def _plain_text(nodes) -> str:
    return "".join(node.text for node in nodes)


def _inline(node: Dict[str, Any]) -> InlineNode:
    tag, content = node["t"], node.get("c", [])
    if tag == "Str":
        return InlineNode(kind=tag, text=content)
    if tag in ("Space", "SoftBreak", "LineBreak"):
        return InlineNode(kind=tag, text=" " if tag == "Space" else "\n")
    if tag in ("Code", "Math"):
        return InlineNode(kind=tag, text=content[-1])
    if tag in ("Link", "Image"):
        children = tuple(_inline(n) for n in content[1])
        return InlineNode(kind=tag, text=_plain_text(children), target=content[2][0], children=children)
    if tag in ("Span", "Cite"):
        children = tuple(_inline(n) for n in content[1])
        return InlineNode(kind=tag, text=_plain_text(children), children=children)
    if tag in ("Emph", "Strong", "Underline", "Strikeout", "Superscript", "Subscript", "SmallCaps", "Quoted"):
        raw_children = content[-1] if tag == "Quoted" else content
        children = tuple(_inline(n) for n in raw_children)
        return InlineNode(kind=tag, text=_plain_text(children), children=children)
    if tag == "RawInline":
        return InlineNode(kind=tag, text=content[-1])
    return InlineNode(kind=tag)


def _block_list(raw_blocks, path: str) -> Tuple[BlockNode, ...]:
    return tuple(_block(item, f"{path}[{i}]") for i, item in enumerate(raw_blocks))


def _table_rows(raw_rows, path: str) -> Tuple[BlockNode, ...]:
    rows = []
    for i, raw in enumerate(raw_rows):
        cells = []
        for j, payload in enumerate(raw[1]):
            cells.append(BlockNode(
                kind="table_cell", source_ref=f"{path}[{i}].cell[{j}]",
                children=_block_list(payload[4], f"{path}[{i}].cell[{j}].blocks"),
                row_span=payload[2], col_span=payload[3],
            ))
        rows.append(BlockNode(kind="table_row", source_ref=f"{path}[{i}]", children=tuple(cells)))
    return tuple(rows)


def _table_blocks(data, path: str) -> Tuple[BlockNode, ...]:
    """Pandoc 2.10+ Table: attr, caption, colspecs, head, bodies, foot."""
    if len(data) != 6:
        return ()
    rows = []
    head = data[3][1]
    rows.extend(_table_rows(head, f"{path}.head"))
    for i, body in enumerate(data[4]):
        body_payload = body
        rows.extend(_table_rows(body_payload[2], f"{path}.body[{i}].head"))
        rows.extend(_table_rows(body_payload[3], f"{path}.body[{i}].rows"))
    rows.extend(_table_rows(data[5][1], f"{path}.foot"))
    return tuple(rows)


def _block(node: Dict[str, Any], ref: str) -> BlockNode:
    tag = node["t"]
    data = node.get("c", [])
    if tag == "Header":
        inlines = tuple(_inline(item) for item in data[2])
        return BlockNode(kind="heading", source_ref=ref, level=data[0], inlines=inlines, text=_plain_text(inlines))
    if tag in ("Para", "Plain"):
        inlines = tuple(_inline(item) for item in data)
        return BlockNode(kind="paragraph", source_ref=ref, inlines=inlines, text=_plain_text(inlines))
    if tag in ("BulletList", "OrderedList"):
        entries = data[1] if tag == "OrderedList" else data
        children = tuple(
            BlockNode(kind="list_item", source_ref=f"{ref}.item[{i}]",
                      children=_block_list(items, f"{ref}.item[{i}].blocks"))
            for i, items in enumerate(entries)
        )
        return BlockNode(kind="ordered_list" if tag == "OrderedList" else "bullet_list",
                         source_ref=ref, children=children)
    if tag in ("BlockQuote",):
        return BlockNode(kind="blockquote", source_ref=ref, children=_block_list(data, f"{ref}.blocks"))
    if tag == "Div":
        return BlockNode(kind="division", source_ref=ref, children=_block_list(data[1], f"{ref}.blocks"))
    if tag == "Figure":
        return BlockNode(kind="figure", source_ref=ref, children=_block_list(data[2], f"{ref}.blocks"))
    if tag == "Table":
        return BlockNode(kind="table", source_ref=ref, children=_table_blocks(data, ref))
    if tag == "CodeBlock":
        return BlockNode(kind="code", source_ref=ref, text=data[1])
    if tag == "RawBlock":
        return BlockNode(kind="raw", source_ref=ref, text=data[-1])
    return BlockNode(kind=tag.lower(), source_ref=ref)


def _walk_features(node, counts, images):
    if isinstance(node, list):
        for part in node:
            _walk_features(part, counts, images)
    elif isinstance(node, dict):
        if isinstance(node.get("t"), str):
            tag = node["t"]
            counts[tag] = counts.get(tag, 0) + 1
            if tag == "Image":
                images.append(node["c"][2][0])
        for part in node.values():
            _walk_features(part, counts, images)


def from_pandoc_ast(ast: Any) -> DocumentIR:
    """Validate and project Pandoc's reader AST; preserve unsupported nodes."""
    if isinstance(ast, (bytes, str)):
        ast = json.loads(ast)
    if not isinstance(ast, dict) or not isinstance(ast.get("pandoc-api-version"), list):
        raise ValueError("Expected a Pandoc JSON document with an API version")
    if not isinstance(ast.get("blocks"), list) or not isinstance(ast.get("meta"), dict):
        raise ValueError("Pandoc document requires 'blocks' and 'meta'")
    if not all(isinstance(x, dict) and isinstance(x.get("t"), str) for x in ast["blocks"]):
        raise ValueError("Invalid Pandoc block node")
    blocks = _block_list(ast["blocks"], "blocks")
    counts, images = {}, []
    _walk_features(ast["blocks"], counts, images)
    return DocumentIR(
        blocks=blocks,
        ast_json=json.dumps(ast, ensure_ascii=False, separators=(",", ":")),
        features=tuple(sorted(counts.items())),
        image_sources=tuple(images),
    )
