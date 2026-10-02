import sys

from app.ingestion.pdf_extractor import extract_pdf_pages


if len(sys.argv) != 2:
    raise SystemExit(
        "Usage: python -m app.ingestion.inspect_pdf <pdf-path>"
    )

pdf_path = sys.argv[1]

pages = extract_pdf_pages(pdf_path)

print(f"Pages extracted: {len(pages)}")

for page in pages[:3]:
    print("\n" + "=" * 80)
    print(f"PAGE {page.page_number}")
    print("=" * 80)
    print(page.text[:2000])
