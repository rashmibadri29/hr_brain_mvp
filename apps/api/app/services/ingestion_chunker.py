import re

from app.models.ingestion import DocumentChunk
from app.services.ingestion_classifier import classify_domain, classify_risk, classify_sensitivity

HEADING_PATTERN = re.compile(r"^(#{1,6}\s+.+|[A-Z][A-Za-z0-9 &/,-]{3,80}:?)$")


def chunk_text(
    *,
    text: str,
    source_document_id: str,
    source_title: str,
    max_chars: int = 1400,
    overlap_chars: int = 180,
) -> list[DocumentChunk]:
    normalized = _normalize_text(text)
    if not normalized:
        return []

    chunks: list[DocumentChunk] = []
    start = 0
    chunk_index = 0
    while start < len(normalized):
        end = min(start + max_chars, len(normalized))
        if end < len(normalized):
            paragraph_break = normalized.rfind("\n\n", start, end)
            sentence_break = normalized.rfind(". ", start, end)
            split_at = max(paragraph_break, sentence_break)
            if split_at > start + int(max_chars * 0.45):
                end = split_at + (1 if split_at == sentence_break else 0)

        content = normalized[start:end].strip()
        if content:
            section_title = _detect_section_title(content)
            domain = classify_domain(content)
            sensitivity = classify_sensitivity(content)
            risk = classify_risk(domain, sensitivity, content)
            chunk_index += 1
            chunks.append(
                DocumentChunk(
                    id=f"{source_document_id}-chunk-{chunk_index}",
                    source_document_id=source_document_id,
                    source_title=source_title,
                    chunk_index=chunk_index,
                    content=content,
                    section_title=section_title,
                    start_char=start,
                    end_char=end,
                    hr_domain=domain,
                    risk_level=risk,
                    sensitivity_label=sensitivity,
                    citation_label=f"{source_title} chunk {chunk_index}",
                )
            )

        if end >= len(normalized):
            break
        start = max(end - overlap_chars, start + 1)

    return chunks


def _normalize_text(text: str) -> str:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    normalized = re.sub(r"[ \t]+", " ", normalized)
    normalized = re.sub(r"\n{3,}", "\n\n", normalized)
    return normalized.strip()


def _detect_section_title(content: str) -> str | None:
    for line in content.splitlines()[:5]:
        clean = line.strip().strip("# ").strip()
        if clean and HEADING_PATTERN.match(line.strip()):
            return clean[:120]
    return None
