"""
PDF Transformer for RAG System.

Handles extraction of text from both text-based and scanned PDFs.
Combines PDF loading with OCR capabilities for scanned documents.
"""

import pdfplumber
import fitz  # PyMuPDF
from pathlib import Path
from typing import List, Dict, Optional
from PIL import Image
import io
import uuid


class PDFTransformer:
    """
    PDF Transformer for loading and processing PDF files.
    Handles both text-based and scanned PDFs with automatic detection.
    """
    
    def __init__(self, ocr_processor=None):
        """
        Initialize the PDF transformer.
        
        Args:
            ocr_processor: Optional OCR processor for scanned PDFs.
                          If not provided, import from image_transformer.
        """
        self.ocr_processor = ocr_processor
        if self.ocr_processor is None:
            try:
                from .image_transformer import OCRProcessor
                self.ocr_processor = OCRProcessor()
            except ImportError:
                print("⚠️  OCR processor not available. Scanned PDFs will be skipped.")
                self.ocr_processor = None
    
    def detect_pdf_type(self, pdf_path: Path) -> str:
        """
        Detect whether PDF is text-based or scanned.
        
        Args:
            pdf_path: Path to PDF file
        
        Returns:
            'text' if text can be extracted, 'scanned' otherwise
        """
        try:
            with pdfplumber.open(pdf_path) as pdf:
                # Check first 3 pages for text
                pages_to_check = min(3, len(pdf.pages))
                total_text = 0
                
                for i in range(pages_to_check):
                    text = pdf.pages[i].extract_text()
                    if text:
                        total_text += len(text.strip())
                
                # If we extracted meaningful text, it's text-based
                return 'text' if total_text > 50 else 'scanned'
        except Exception as e:
            print(f"⚠️  Error detecting PDF type for {pdf_path.name}: {e}")
            return 'scanned'  # Default to scanned if error
    
    def extract_text_pdf(self, pdf_path: Path) -> List[Dict]:
        """
        Extract text from text-based PDF using pdfplumber.
        
        Args:
            pdf_path: Path to PDF file
        
        Returns:
            List of dictionaries with extracted text and metadata
        """
        results = []
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, start=1):
                    text = page.extract_text()
                    
                    if text and text.strip():
                        results.append({
                            'id': str(uuid.uuid4()),
                            'source': pdf_path.name,
                            'page': page_num,
                            'modality': 'pdf',
                            'extraction_method': 'direct',
                            'text': text
                        })
        except Exception as e:
            print(f"⚠️  Error extracting text from {pdf_path.name}: {e}")
        
        return results
    
    def pdf_to_images(self, pdf_path: Path) -> List[tuple]:
        """
        Convert PDF pages to images for OCR processing.
        
        Args:
            pdf_path: Path to PDF file
        
        Returns:
            List of tuples (page_number, PIL.Image)
        """
        images = []
        
        try:
            pdf_document = fitz.open(pdf_path)
            
            for page_num in range(len(pdf_document)):
                page = pdf_document[page_num]
                
                # Convert page to image (72 DPI default, increase for better OCR)
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom = 144 DPI
                
                # Convert to PIL Image
                img_data = pix.tobytes("png")
                img = Image.open(io.BytesIO(img_data))
                
                images.append((page_num + 1, img))
            
            pdf_document.close()
        except Exception as e:
            print(f"⚠️  Error converting PDF to images for {pdf_path.name}: {e}")
        
        return images
    
    def load_pdf(self, pdf_path: Path) -> List[Dict]:
        """
        Main PDF loading function. Detects type and routes to appropriate handler.
        
        Args:
            pdf_path: Path to PDF file
        
        Returns:
            List of extraction results with metadata
        """
        print(f"📄 Processing: {pdf_path.name}")
        
        pdf_type = self.detect_pdf_type(pdf_path)
        print(f"   Type: {pdf_type}")
        
        if pdf_type == 'text':
            results = self.extract_text_pdf(pdf_path)
            print(f"   ✅ Extracted {len(results)} pages (direct)")
        else:
            # Scanned PDF - convert to images and OCR
            if self.ocr_processor is None:
                print("   ⚠️  OCR processor not available, skipping scanned PDF")
                return []
            
            images = self.pdf_to_images(pdf_path)
            results = []
            
            for page_num, img in images:
                text = self.ocr_processor.ocr_image(img)
                
                if text and text.strip():
                    results.append({
                        'id': str(uuid.uuid4()),
                        'source': pdf_path.name,
                        'page': page_num,
                        'modality': 'pdf',
                        'extraction_method': 'ocr',
                        'text': text
                    })
            
            print(f"   ✅ Extracted {len(results)} pages (OCR)")
        
        return results
    
    def load_pdfs_batch(self, pdf_dir: Path) -> List[Dict]:
        """
        Load all PDFs from a directory.
        
        Args:
            pdf_dir: Directory containing PDF files
        
        Returns:
            List of extraction results
        """
        results = []
        
        # Get all PDF files
        pdf_files = []
        if pdf_dir.exists():
            pdf_files.extend(pdf_dir.glob('*.pdf'))
            pdf_files.extend(pdf_dir.glob('*.PDF'))
        
        print(f"\n📚 Found {len(pdf_files)} PDF(s) in {pdf_dir.name}")
        
        for pdf_path in sorted(pdf_files):
            result = self.load_pdf(pdf_path)
            results.extend(result)
        
        return results
    
    def transform(self, pdf_input) -> List[Dict]:
        """
        Main transformation method. Accepts Path or directory.
        
        Args:
            pdf_input: Path to PDF file or directory
        
        Returns:
            List of extraction results
        """
        if isinstance(pdf_input, str):
            pdf_input = Path(pdf_input)
        
        if pdf_input.is_file():
            return self.load_pdf(pdf_input)
        elif pdf_input.is_dir():
            return self.load_pdfs_batch(pdf_input)
        else:
            print(f"❌ Invalid input: {pdf_input}")
            return []
