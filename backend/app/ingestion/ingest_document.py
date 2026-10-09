import argparse
from pathlib import Path

from app.ingestion.pdf_extractor import extract_pdf_pages
from app.ingestion.profiles import DOCUMENT_PROFILES
from app.ingestion.pipeline import persist_document
from app.ingestion.ucb_cyber_chunker import (
    chunk_ucb_cyber_pages,
    normalize_ucb_chunks,
)


CHUNKERS = {
    "ucb_cyber": lambda pages: normalize_ucb_chunks(
        chunk_ucb_cyber_pages(pages)
    ),
}


def ingest_profiled_pdf(
    pdf_path: str | Path,
    *,
    dry_run: bool = False,
):
    pdf_path = Path(pdf_path)

    if not pdf_path.is_file():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    profile = DOCUMENT_PROFILES.get(pdf_path.name)

    if profile is None:
        known = ", ".join(sorted(DOCUMENT_PROFILES))
        raise ValueError(
            f"No document profile found for {pdf_path.name!r}. "
            f"Known profiles: {known or '(none)'}"
        )

    chunker = CHUNKERS.get(profile.chunker)

    if chunker is None:
        raise ValueError(
            f"No chunking strategy registered for {profile.chunker!r}."
        )

    pages = extract_pdf_pages(pdf_path)
    chunks = chunker(pages)

    return persist_document(
        pdf_path,
        profile,
        chunks,
        dry_run=dry_run,
        page_count=len(pages),
    )


def main():
    parser = argparse.ArgumentParser(
        description="Ingest a PDF using its registered document profile."
    )
    parser.add_argument("pdf_path")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate and report chunks without writing to the database.",
    )
    args = parser.parse_args()

    ingest_profiled_pdf(args.pdf_path, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
