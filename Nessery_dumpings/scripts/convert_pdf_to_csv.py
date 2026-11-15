"""
Convert raw e-GP PDF manuals into structured CSV files:
1. data/raw/egp_manual.pdf -> data/processed/egp_manual_extracted.csv
2. data/raw/eGP_NewUserRegManual_English.pdf -> data/processed/egp_registration_manual_extracted.csv
"""

import csv
import re
from pathlib import Path
import fitz  # PyMuPDF

BASE_DIR = Path('e:/E-gp Project manual')
RAW_DIR = BASE_DIR / 'data' / 'raw'
PROCESSED_DIR = BASE_DIR / 'data' / 'processed'
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

def clean_text(text: str) -> str:
    """Clean extracted PDF text into single-line clean text for CSV."""
    if not text:
        return ''
    # Replace line breaks with spaces
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    cleaned = ' '.join(lines)
    # Remove excessive whitespace
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned

def extract_pdf_to_csv(pdf_path: Path, csv_path: Path, source_name: str):
    print(f"Opening {pdf_path.name}...")
    doc = fitz.open(str(pdf_path))
    total_pages = len(doc)
    print(f"Total pages in {pdf_path.name}: {total_pages}")
    
    rows = []
    current_chapter = "General / Introduction"
    
    chapter_regex = re.compile(r'^(Chapter|Section|Module)\s+(\d+[:.]?\s*.*)', re.IGNORECASE)
    
    for page_idx in range(total_pages):
        page_num = page_idx + 1
        page = doc[page_idx]
        raw_text = page.get_text()
        
        # Check for chapter/section header in top lines
        lines = [l.strip() for l in raw_text.split('\n') if l.strip()]
        for l in lines[:5]:
            m = chapter_regex.match(l)
            if m:
                current_chapter = l[:100]
                break
            # Also detect common e-GP module headers
            if any(kw in l.lower() for kw in ['annual procurement plan', 'tender preparation', 'tender opening', 'tender evaluation', 'contract management', 'complaint', 'registration', 'user management']):
                if len(l) < 80:
                    current_chapter = l
                    break

        cleaned_content = clean_text(raw_text)
        image_list = page.get_images()
        
        rows.append({
            'page_number': page_num,
            'source_file': source_name,
            'detected_section': current_chapter,
            'text_content': cleaned_content,
            'char_count': len(cleaned_content),
            'word_count': len(cleaned_content.split()),
            'image_count': len(image_list)
        })
        
        if page_num % 100 == 0 or page_num == total_pages:
            print(f"  Processed {page_num}/{total_pages} pages...")

    fieldnames = ['page_number', 'source_file', 'detected_section', 'text_content', 'char_count', 'word_count', 'image_count']
    
    with open(csv_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
        
    print(f"Successfully saved {len(rows)} pages to {csv_path.name}")
    print(f"  File size: {csv_path.stat().st_size:,} bytes\n")

def main():
    print("=" * 60)
    print("EXTRACTING RAW PDF MANUALS TO STRUCTURED CSV")
    print("=" * 60)
    
    # 1. PE User Manual (543 pages)
    pe_manual_pdf = RAW_DIR / 'egp_manual.pdf'
    pe_manual_csv = PROCESSED_DIR / 'egp_manual_extracted.csv'
    extract_pdf_to_csv(pe_manual_pdf, pe_manual_csv, 'e-GP System User Manual (PE)')
    
    # Also save copy in root for easy user access
    root_pe_csv = BASE_DIR / 'egp_manual_extracted.csv'
    extract_pdf_to_csv(pe_manual_pdf, root_pe_csv, 'e-GP System User Manual (PE)')
    
    # 2. Tenderer / New User Registration Manual (27 pages)
    reg_manual_pdf = RAW_DIR / 'eGP_NewUserRegManual_English.pdf'
    reg_manual_csv = PROCESSED_DIR / 'egp_registration_manual_extracted.csv'
    if reg_manual_pdf.exists():
        extract_pdf_to_csv(reg_manual_pdf, reg_manual_csv, 'e-GP New User Registration Manual (Tenderer)')

    print("PDF to CSV extraction complete!")

if __name__ == '__main__':
    main()
