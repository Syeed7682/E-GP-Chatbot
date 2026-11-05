"""
Document Loader Service.
Responsible for reading raw PDF manual files and extracting text per page.
"""
import os
import re
from typing import List, Dict
from pypdf import PdfReader

def clean_text(text: str) -> str:
    """
    Cleans raw extracted text:
    - Normalizes excessive whitespace and newlines
    - Removes non-printable control characters
    """
    if not text:
        return ""
    # Strip whitespace line by line and collapse excessive blank lines
    lines = [re.sub(r'[ \t]+', ' ', line).strip() for line in text.splitlines()]
    # Remove consecutive empty lines
    cleaned_lines = []
    prev_empty = False
    for line in lines:
        if line:
            cleaned_lines.append(line)
            prev_empty = False
        elif not prev_empty:
            cleaned_lines.append("")
            prev_empty = True
    return "\n".join(cleaned_lines).strip()

def load_pdf(file_path: str, extract_images: bool = True, images_dir: str = "data/extracted_images") -> List[Dict]:
    """
    Extracts text and embedded portal screenshots from a single PDF manual, page by page.
    
    Args:
        file_path: Absolute or relative path to the PDF file.
        extract_images: Whether to extract and save page screenshots/diagrams.
        images_dir: Output folder for extracted images.
        
    Returns:
        List of dictionaries with keys:
            - source: name of the file
            - page: page number (1-indexed)
            - text: extracted text
            - image_path: path to primary extracted image on that page (if any)
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"PDF file not found: {file_path}")

    filename = os.path.basename(file_path)
    documents = []
    
    if extract_images:
        os.makedirs(images_dir, exist_ok=True)

    try:
        reader = PdfReader(file_path)
        total_pages = len(reader.pages)
        print(f"[document_loader] Reading '{filename}' ({total_pages} pages)...")
        for page_index, page in enumerate(reader.pages):
            page_num = page_index + 1
            raw_text = page.extract_text() or ""
            cleaned = clean_text(raw_text)

            image_path = None
            if extract_images and len(page.images) > 0:
                try:
                    # Pick largest image on page (usually the portal screenshot)
                    best_img = None
                    best_size = 0
                    for img in page.images:
                        if len(img.data) > best_size and len(img.data) > 8192:  # at least 8KB
                            best_size = len(img.data)
                            best_img = img

                    if best_img is not None:
                        out_img_path = os.path.join(images_dir, f"page_{page_num}.jpg")
                        if not os.path.exists(out_img_path):
                            with open(out_img_path, "wb") as f_img:
                                f_img.write(best_img.data)
                        image_path = out_img_path
                except Exception as e_img:
                    pass  # Gracefully proceed if image decoding fails

            if cleaned or image_path:
                documents.append({
                    "source": filename,
                    "page": page_num,
                    "text": cleaned,
                    "image_path": image_path
                })

            if page_num % 100 == 0 or page_num == total_pages:
                print(f"[document_loader] Extracted {page_num}/{total_pages} pages...")
        print(f"[document_loader] Finished '{filename}': {len(documents)} valid pages extracted.")
    except Exception as e:
        print(f"[document_loader] Error reading {file_path}: {e}")
        raise e

    return documents

def load_all_documents(raw_dir: str = "data/raw") -> List[Dict]:
    """
    Scans the raw directory and loads all supported PDF files.
    
    Args:
        raw_dir: Directory containing raw manual PDFs.
        
    Returns:
        List of document page dicts across all files.
    """
    all_pages: List[Dict] = []
    
    if not os.path.exists(raw_dir):
        print(f"[document_loader] Raw directory '{raw_dir}' does not exist.")
        return all_pages

    files = [f for f in os.listdir(raw_dir) if f.lower().endswith(".pdf")]
    if not files:
        print(f"[document_loader] No PDF files found in '{raw_dir}'.")
        return all_pages

    print(f"[document_loader] Found {len(files)} PDF file(s) in '{raw_dir}'.")
    for file in files:
        full_path = os.path.join(raw_dir, file)
        pages = load_pdf(full_path)
        all_pages.extend(pages)

    return all_pages

if __name__ == "__main__":
    # Test execution
    docs = load_all_documents("data/raw")
    print(f"Total pages extracted: {len(docs)}")
    if docs:
        print("Sample extracted text:")
        print(docs[0]["text"][:200] + "...")
