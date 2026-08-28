"""Header-aware markdown chunker preserving semantic hierarchy and breadcrumbs."""

import re
from typing import List, Tuple
from devbrain.engine.models import Document, DocumentChunk

HEADING_PATTERN = re.compile(r"^(#{1,6})\s+(.*)$")


def chunk_document(
    doc: Document,
    max_chunk_chars: int = 1500,
    overlap_chars: int = 200,
) -> List[DocumentChunk]:
    """Split a Document into header-aware hierarchical chunks."""
    lines = doc.raw_content.splitlines()
    if not lines or not doc.raw_content.strip():
        return [
            DocumentChunk(
                chunk_id=f"{doc.doc_id}#0",
                doc_id=doc.doc_id,
                file_path=doc.file_path,
                title=doc.title,
                header_path="",
                content=f"# {doc.title}\n(Empty document)",
                tags=doc.tags,
                chunk_index=0,
            )
        ]

    sections: List[Tuple[str, List[str]]] = []  # (header_path, lines)
    header_stack: List[Tuple[int, str]] = []  # (level, text)
    current_section_lines: List[str] = []

    def get_current_breadcrumb() -> str:
        # Exclude Level 1 heading if it is identical to doc.title
        filtered = [
            h[1] for h in header_stack
            if not (h[0] == 1 and h[1].lower() == doc.title.lower())
        ]
        return " > ".join(filtered)

    for line in lines:
        heading_match = HEADING_PATTERN.match(line.strip())
        if heading_match:
            if current_section_lines and any(l.strip() for l in current_section_lines):
                sections.append((get_current_breadcrumb(), current_section_lines))
                current_section_lines = []

            level = len(heading_match.group(1))
            heading_text = heading_match.group(2).strip()

            while header_stack and header_stack[-1][0] >= level:
                header_stack.pop()

            header_stack.append((level, heading_text))
            current_section_lines.append(line)
        else:
            current_section_lines.append(line)

    if current_section_lines and any(l.strip() for l in current_section_lines):
        sections.append((get_current_breadcrumb(), current_section_lines))

    chunks: List[DocumentChunk] = []
    chunk_counter = 0

    for header_path, sec_lines in sections:
        sec_text = "\n".join(sec_lines).strip()
        if not sec_text:
            continue

        if header_path:
            breadcrumb_header = f"[{doc.title}] > {header_path}"
        else:
            breadcrumb_header = f"[{doc.title}]"

        if len(sec_text) <= max_chunk_chars:
            chunk_content = f"{breadcrumb_header}\n\n{sec_text}"
            chunks.append(
                DocumentChunk(
                    chunk_id=f"{doc.doc_id}#{chunk_counter}",
                    doc_id=doc.doc_id,
                    file_path=doc.file_path,
                    title=doc.title,
                    header_path=header_path,
                    content=chunk_content,
                    tags=doc.tags,
                    chunk_index=chunk_counter,
                )
            )
            chunk_counter += 1
        else:
            paragraphs = sec_text.split("\n\n")
            curr_subchunk: List[str] = []
            curr_subchunk_len = 0

            for p in paragraphs:
                p_len = len(p) + 2
                if curr_subchunk_len + p_len > max_chunk_chars and curr_subchunk:
                    subchunk_body = "\n\n".join(curr_subchunk)
                    chunk_content = f"{breadcrumb_header}\n\n{subchunk_body}"
                    chunks.append(
                        DocumentChunk(
                            chunk_id=f"{doc.doc_id}#{chunk_counter}",
                            doc_id=doc.doc_id,
                            file_path=doc.file_path,
                            title=doc.title,
                            header_path=header_path,
                            content=chunk_content,
                            tags=doc.tags,
                            chunk_index=chunk_counter,
                        )
                    )
                    chunk_counter += 1
                    curr_subchunk = [p]
                    curr_subchunk_len = p_len
                else:
                    curr_subchunk.append(p)
                    curr_subchunk_len += p_len

            if curr_subchunk:
                subchunk_body = "\n\n".join(curr_subchunk)
                chunk_content = f"{breadcrumb_header}\n\n{subchunk_body}"
                chunks.append(
                    DocumentChunk(
                        chunk_id=f"{doc.doc_id}#{chunk_counter}",
                        doc_id=doc.doc_id,
                        file_path=doc.file_path,
                        title=doc.title,
                        header_path=header_path,
                        content=chunk_content,
                        tags=doc.tags,
                        chunk_index=chunk_counter,
                    )
                )
                chunk_counter += 1

    return chunks
