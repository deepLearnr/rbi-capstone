import sys

from app.ingestion.faq_chunker import chunk_faq_pages
from app.ingestion.pdf_extractor import extract_pdf_pages


if len(sys.argv) != 2:
    raise SystemExit(
        "Usage: python -m app.ingestion.inspect_chunks <pdf-path>"
    )

pdf_path = sys.argv[1]

pages = extract_pdf_pages(pdf_path)
chunks = chunk_faq_pages(pages)

print(f"Pages: {len(pages)}")
print(f"FAQ chunks: {len(chunks)}")

for chunk in chunks:
    print("\n" + "=" * 80)
    print(
        f"CHUNK {chunk.chunk_index} | "
        f"Q{chunk.question_number} | "
        f"pages {chunk.page_start}-{chunk.page_end}"
    )
    print("=" * 80)
    print(chunk.content[:1200])
