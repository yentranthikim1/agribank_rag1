from __future__ import annotations

import argparse
import asyncio
import json
import os
import re
import unicodedata
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parents[1]
DATADIR = ROOT_DIR / "datademo"
OUTPUT_DIR = ROOT_DIR / "storage" / "output"
load_dotenv(ROOT_DIR / "src" / ".env", override=False)


def normalize_unicode(text: str) -> str:
    """Normalize Vietnamese text to NFC form and fix common encoding issues."""
    if text is None:
        return ""
    
    # First normalize to NFC
    normalized = unicodedata.normalize("NFC", text)
    
    # Clean up common encoding issues
    normalized = normalized.replace("\ufeff", "")  # Remove BOM
    normalized = normalized.replace("\ufffd", "?")  # Replace replacement char with ?
    
    # Normalize multiple spaces/newlines
    normalized = re.sub(r"[ \t]+", " ", normalized)  # Multiple spaces → single space
    normalized = re.sub(r"\n\s*\n+", "\n\n", normalized)  # Multiple newlines → double newline
    
    return normalized.strip()


def contains_unusual_characters(text: str) -> bool:
    """Check for invalid or replacement characters in text."""
    if not text:
        return True
    
    # Check for Unicode replacement character
    weird = ["�", "\ufffd", "\uFFFD", "\uffef"]
    if any(marker in text for marker in weird):
        return True
    
    # Check for null bytes
    if "\x00" in text:
        return True
    
    # Check for too many control characters (except newline, tab)
    control_chars = sum(1 for c in text if ord(c) < 32 and c not in "\n\t\r")
    if control_chars > len(text) * 0.1:  # More than 10% control chars
        return True
    
    return False


def ensure_output_dir() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def render_pdf_pages_to_images(pdf_path: Path) -> List[Path]:
    images: List[Path] = []
    try:
        import fitz
    except Exception:
        return images

    try:
        doc = fitz.open(str(pdf_path))
    except Exception:
        return images

    ensure_output_dir()
    for page_index in range(doc.page_count):
        page = doc[page_index]
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
        image_path = OUTPUT_DIR / f"{pdf_path.stem}_page_{page_index + 1}.png"
        pix.save(str(image_path))
        images.append(image_path)
    doc.close()
    return images


def is_placeholder_api_key(value: str) -> bool:
    if value is None:
        return True
    cleaned = unicodedata.normalize("NFC", str(value)).strip().strip("'\"")
    if not cleaned:
        return True
    needle = cleaned.lower()
    placeholder_tokens = (
        "key của bạn",
        "key cua ban",
        "your_key_here",
        "placeholder",
        "example_key",
        "<your_api_key>",
    )
    return needle in placeholder_tokens or needle.startswith("key của bạn") or needle.startswith("key cua ban")


def read_key_status() -> Dict[str, Any]:
    key_name = "LLAMA_CLOUD_API_KEY"
    raw_value = os.environ.get(key_name, "")
    present = bool(raw_value.strip()) and not is_placeholder_api_key(raw_value)
    return {
        "key_name": key_name,
        "present": present,
        "warning": "Key exists but value is not printed by design." if present else "No active key found in environment.",
    }


def extract_text_from_pdf(pdf_path: Path) -> Tuple[List[Dict[str, Any]], List[str]]:
    records: List[Dict[str, Any]] = []
    warnings: List[str] = []
    try:
        import fitz
    except Exception as exc:
        return [], [f"PyMuPDF unavailable: {exc}"]

    try:
        doc = fitz.open(str(pdf_path))
    except Exception as exc:
        return [], [f"Could not open PDF with PyMuPDF: {exc}"]

    page_count = doc.page_count
    for page_index in range(page_count):
        page = doc[page_index]
        page_num = page_index + 1
        text = ""
        try:
            text = page.get_text("text")
        except Exception as exc:
            warnings.append(f"Page {page_num} of {pdf_path.name}: pymupdf text extraction failed: {exc}")
            text = ""

        normalized = normalize_unicode(text)
        if not normalized.strip() or contains_unusual_characters(normalized):
            warnings.append(
                f"Page {page_num} of {pdf_path.name}: empty or malformed text from PyMuPDF; fallback required."
            )
            records.append(
                {
                    "source": str(pdf_path),
                    "page": page_num,
                    "text": "",
                    "ocr_used": "pymupdf_failed",
                    "language": "vi",
                    "status": "fallback_needed",
                    "warning": warnings[-1],
                }
            )
        else:
            records.append(
                {
                    "source": str(pdf_path),
                    "page": page_num,
                    "text": normalized,
                    "ocr_used": "pymupdf",
                    "language": "vi",
                    "status": "ok",
                    "warning": "",
                }
            )

    doc.close()
    return records, warnings


async def llama_parse_pdf(pdf_path: Path) -> str:
    key_status = read_key_status()
    if not key_status["present"]:
        raise RuntimeError("LLAMA_CLOUD_API_KEY is missing or placeholder; remote OCR is skipped.")

    try:
        from llama_cloud import AsyncLlamaCloud
    except Exception as exc:
        raise RuntimeError(f"llama_cloud package not available: {exc}") from exc

    api_key = os.environ.get("LLAMA_CLOUD_API_KEY", "")
    if not api_key.strip() or is_placeholder_api_key(api_key):
        raise RuntimeError("LLAMA_CLOUD_API_KEY is empty or placeholder; remote OCR disabled.")

    client = AsyncLlamaCloud(api_key=api_key)
    file_obj = await client.files.create(file=str(pdf_path), purpose="parse")
    result = await client.parsing.parse(
        file_id=file_obj.id,
        tier="agentic",
        version="latest",
        expand=["markdown_full"],
    )
    markdown = getattr(result, "markdown_full", None) or getattr(result, "text", "") or ""
    return normalize_unicode(markdown)


def fallback_to_llama_parse(pdf_path: Path, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    if not records:
        return records

    updated: List[Dict[str, Any]] = []
    page_map = {item["page"]: item for item in records if item.get("status") == "fallback_needed"}
    if not page_map:
        return records

    key_status = read_key_status()
    if not key_status["present"]:
        for item in records:
            if item.get("status") == "fallback_needed":
                item["ocr_used"] = "warning_only"
                item["status"] = "warning_no_ocr"
                item["warning"] = "Remote OCR unavailable because key is absent; document remains raw fallback warning."
            updated.append(item)
        return updated

    try:
        fallback_text = asyncio.run(llama_parse_pdf(pdf_path))
    except Exception as exc:
        for item in records:
            if item.get("status") == "fallback_needed":
                item["ocr_used"] = "warning_only"
                item["status"] = "warning_no_ocr"
                item["warning"] = f"LLAMAPARSE failed: {exc}"
            updated.append(item)
        return updated

    pages_with_text = split_llama_markdown_into_pages(fallback_text, total_pages=len(page_map))
    for item in records:
        if item.get("status") == "fallback_needed":
            page_num = item["page"]
            page_text = pages_with_text.get(page_num, "")
            if page_text and not contains_unusual_characters(page_text):
                item["text"] = page_text
                item["ocr_used"] = "llama_cloud"
                item["status"] = "ok"
                item["warning"] = "Recovered via LlamaParse after PyMuPDF fallback."
            else:
                item["ocr_used"] = "warning_only"
                item["status"] = "warning_no_ocr"
                item["warning"] = "LlamaParse returned empty or invalid text; no reliable OCR text was stored."
        updated.append(item)
    return updated


def split_llama_markdown_into_pages(markdown_text: str, total_pages: int) -> Dict[int, str]:
    mapping: Dict[int, str] = {}
    if not markdown_text.strip():
        return mapping

    cleaned = markdown_text.replace("\r\n", "\n")
    segments = re.split(r"(?im)^(?:Page\s+\d+|Trang\s+\d+)\s*$", cleaned)
    if len(segments) > 1:
        for idx, segment in enumerate(segments, start=1):
            if idx <= total_pages:
                mapping[idx] = normalize_unicode(segment.strip())
        return mapping

    lines = cleaned.split("\n")
    page_size = max(1, len(lines) // max(1, total_pages))
    for page_index in range(total_pages):
        start = page_index * page_size
        end = (page_index + 1) * page_size if page_index < total_pages - 1 else len(lines)
        page_text = "\n".join(lines[start:end]).strip()
        mapping[page_index + 1] = normalize_unicode(page_text)
    return mapping


def fixed_size_chunks(text: str, chunk_size: int = 1200, overlap: int = 150) -> List[str]:
    if not text:
        return []
    chunks: List[str] = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk = text[start:end]
        chunks.append(chunk.strip())
        if end == len(text):
            break
        start = max(0, end - overlap)
    return [chunk for chunk in chunks if chunk]


def semantic_chunks(text: str, max_chars: int = 1500) -> List[str]:
    if not text:
        return []

    chunks: List[str] = []
    current = ""

    for paragraph in re.split(r"\n\s*\n+", text.strip()):
        cleaned = paragraph.strip()
        if not cleaned:
            continue

        sentences = re.split(
            r"(?<=[.!?])\s+(?=[A-ZÀ-ỿĀ-ſƀ-ƿǀ-ǿȀ-ȿɀ-ɏɐ-ɑ])",
            cleaned
        )
        if len(sentences) == 1:
            sentences = [cleaned]

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            if not current:
                current = sentence
            elif len(current) + 1 + len(sentence) <= max_chars:
                current = f"{current} {sentence}"
            else:
                chunks.append(current.strip())
                current = sentence

    if current:
        chunks.append(current.strip())

    if not chunks:
        return []

    final_chunks: List[str] = []
    for chunk in chunks:
        if len(chunk) <= max_chars:
            final_chunks.append(chunk)
            continue
        for part in fixed_size_chunks(chunk, chunk_size=max_chars, overlap=max_chars // 4):
            if part.strip():
                final_chunks.append(part.strip())
    return final_chunks


def hierarchical_chunks(text: str) -> List[str]:
    if not text:
        return []

    lines = [line.rstrip() for line in text.splitlines()]
    heading_pattern = re.compile(
        r"^(?:chương|mục|điều|khoản|điểm|chủ đề|phần|bộ|ngành|ngôn ngữ|section|chapter|item|point)\s*[:\-]?\s*.*$",
        flags=re.IGNORECASE | re.UNICODE,
    )

    sections: List[Tuple[str | None, List[str]]] = []
    current_heading: str | None = None
    current_lines: List[str] = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            if current_lines:
                sections.append((current_heading, current_lines[:]))
                current_lines = []
            continue

        if heading_pattern.match(stripped):
            if current_lines:
                sections.append((current_heading, current_lines[:]))
                current_lines = []
            current_heading = stripped
            continue

        current_lines.append(stripped)

    if current_lines:
        sections.append((current_heading, current_lines[:]))

    if not any(heading is not None for heading, _ in sections):
        return semantic_chunks(text, max_chars=1800)

    chunks: List[str] = []
    for heading, lines_in_section in sections:
        block = "\n".join(lines_in_section).strip()
        if not block:
            continue
        if heading:
            chunks.append(f"{heading}\n{block}".strip())
        else:
            chunks.append(block)
    return [chunk for chunk in chunks if chunk]


def make_chunk_record(chunk_id: str, strategy: str, source: str, page_start: int, page_end: int, text: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "chunk_id": chunk_id,
        "strategy": strategy,
        "source": source,
        "page_start": page_start,
        "page_end": page_end,
        "text": text,
        "metadata": metadata,
    }


def build_chunks_for_strategy(strategy: str, source: str, page_start: int, page_end: int, text: str) -> List[Dict[str, Any]]:
    if strategy == "fixed_size":
        parts = fixed_size_chunks(text, chunk_size=1200, overlap=200)
    elif strategy == "semantic":
        parts = semantic_chunks(text, max_chars=1200)
    elif strategy == "hierarchical":
        parts = hierarchical_chunks(text)
    else:
        parts = [text]

    chunks: List[Dict[str, Any]] = []
    for idx, chunk in enumerate(parts, start=1):
        metadata: Dict[str, Any] = {"chunk_length": len(chunk), "page_range": [page_start, page_end]}
        if strategy == "hierarchical":
            heading = chunk.splitlines()[0].strip() if chunk.splitlines() else ""
            metadata["heading_hint"] = heading
        chunks.append(make_chunk_record(f"{strategy}-{page_start}-{idx}", strategy, source, page_start, page_end, chunk, metadata))
    return chunks


def summarize_chunks(chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
    lengths = [len(item["text"]) for item in chunks]
    if not lengths:
        return {"count": 0, "min": 0, "max": 0, "avg": 0.0}
    return {
        "count": len(chunks),
        "min": min(lengths),
        "max": max(lengths),
        "avg": round(sum(lengths) / len(lengths), 2),
    }


def process_pdf(pdf_path: Path, write_output: bool = False) -> Dict[str, Any]:
    records, warnings = extract_text_from_pdf(pdf_path)
    if not records:
        return {"source": str(pdf_path), "warnings": warnings, "pages": []}

    records = fallback_to_llama_parse(pdf_path, records)

    page_text_map: Dict[int, str] = {}
    for rec in records:
        if rec.get("status") == "ok":
            page_text_map[rec["page"]] = rec["text"]

    strategies = ["fixed_size", "semantic", "hierarchical"]
    all_chunks: List[Dict[str, Any]] = []
    strategy_summary: Dict[str, Any] = {}

    for strategy in strategies:
        strategy_chunks: List[Dict[str, Any]] = []
        for page_num, text in sorted(page_text_map.items()):
            if not text.strip():
                continue
            strategy_chunks.extend(build_chunks_for_strategy(strategy, str(pdf_path), page_num, page_num, text))
        strategy_summary[strategy] = summarize_chunks(strategy_chunks)
        all_chunks.extend(strategy_chunks)

    if write_output:
        ensure_output_dir()
        output_payload = {
            "source": str(pdf_path),
            "warnings": warnings,
            "records": records,
            "strategies": strategy_summary,
            "chunks": all_chunks,
        }
        json_path = OUTPUT_DIR / f"{pdf_path.stem}_result.json"
        with open(json_path, "w", encoding="utf-8") as handle:
            json.dump(output_payload, handle, ensure_ascii=False, indent=2)

    return {
        "source": str(pdf_path),
        "warnings": warnings,
        "pages": records,
        "strategies": strategy_summary,
        "chunks": all_chunks,
    }


def build_cli() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="OCR + chunking demo for Vietnamese PDF in Buoi 5")
    parser.add_argument("--pdf", type=str, default="", help="Specific PDF path to process. Default: all PDFs in datademo/")
    parser.add_argument("--dry-run", action="store_true", help="Print summary without writing output files")
    parser.add_argument("--write", action="store_true", help="Write raw OCR and chunk report to storage/output")
    return parser


def main() -> int:
    parser = build_cli()
    args = parser.parse_args()

    pdfs = [Path(args.pdf)] if args.pdf else sorted(DATADIR.glob("*.pdf"))
    if not pdfs:
        print("No PDF files found in datademo/. Nothing to process.")
        return 0

    write_output = bool(args.write)
    if args.dry_run and args.write:
        print("Choose either --dry-run or --write, not both.")
        return 2

    for pdf_path in pdfs:
        if not pdf_path.exists():
            print(f"Missing PDF file: {pdf_path}")
            continue

        print(f"Processing: {pdf_path.name}")
        result = process_pdf(pdf_path, write_output=write_output)
        print(json.dumps({
            "source": pdf_path.name,
            "warnings": result.get("warnings", []),
            "strategies": result.get("strategies", {}),
        }, ensure_ascii=False, indent=2))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
