from pathlib import Path

from evaluator.models import Chunk

SUPPORTED_TYPES = {"pdf", "pptx"}


def detect_type(filename: str) -> str:
    suffix = Path(filename).suffix.lower().lstrip(".")
    if suffix not in SUPPORTED_TYPES:
        raise ValueError(f"Unsupported file type: {suffix}")
    return suffix


def extract_chunks(path: str | Path, file_type: str) -> list[Chunk]:
    if file_type == "pdf":
        return _extract_pdf(Path(path))
    if file_type == "pptx":
        return _extract_pptx(Path(path))
    raise ValueError(f"Unsupported file type: {file_type}")


def _extract_pdf(path: Path) -> list[Chunk]:
    from pypdf import PdfReader

    reader = PdfReader(str(path))
    return [Chunk(slide_no=i, content=page.extract_text() or "") for i, page in enumerate(reader.pages, start=1)]


def _extract_pptx(path: Path) -> list[Chunk]:
    from pptx import Presentation

    presentation = Presentation(str(path))
    chunks = []
    for i, slide in enumerate(presentation.slides, start=1):
        parts = []
        for shape in slide.shapes:
            if shape.has_text_frame:
                parts.append(shape.text_frame.text)
        if slide.has_notes_slide and slide.notes_slide.notes_text_frame is not None:
            parts.append(slide.notes_slide.notes_text_frame.text)
        chunks.append(Chunk(slide_no=i, content="\n".join(p for p in parts if p.strip())))
    return chunks
