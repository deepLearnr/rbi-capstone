import sys

from app.ingestion.pdf_extractor import extract_pdf_pages
from app.ingestion.regulatory_chunker import chunk_regulatory_pages


if len(sys.argv) != 2:
    raise SystemExit(
        "Usage: python -m app.ingestion.inspect_regulatory_chunks <pdf-path>"
    )

pdf_path = sys.argv[1]

pages = extract_pdf_pages(pdf_path)
chunks = chunk_regulatory_pages(pages)

print(f"Pages extracted: {len(pages)}")
print(f"Chunks generated: {len(chunks)}")

for chunk in chunks:
    print("\n" + "=" * 80)
    print(
        f"CHUNK {chunk.chunk_index} | "
        f"SECTION {chunk.section_reference} | "
        f"PAGES {chunk.page_start}-{chunk.page_end}"
    )
    print("=" * 80)
    print(f"HEADING: {chunk.heading}")
    print(f"HEADING PATH: {chunk.heading_path}")
    print()
    print(chunk.content)
