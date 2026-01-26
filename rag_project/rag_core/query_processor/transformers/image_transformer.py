"""
Image Transformer for RAG System.

Handles image loading, preprocessing, and OCR text extraction.
Combines functionality from image_loader and OCR modules.
"""

import cv2
import numpy as np
from PIL import Image
from pathlib import Path
from typing import List, Dict, Optional
import uuid
import pytesseract
import warnings

# Configure Tesseract path for Windows
import platform
if platform.system() == 'Windows':
    tesseract_paths = [
        r'C:\Program Files\Tesseract-OCR\tesseract.exe',
        r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
    ]
    for tess_path in tesseract_paths:
        if Path(tess_path).exists():
            pytesseract.pytesseract.tesseract_cmd = tess_path
            break

# Suppress warnings
warnings.filterwarnings('ignore')

# Try to import easyocr (optional fallback)
try:
    import easyocr
    EASYOCR_AVAILABLE = True
    _easyocr_reader = None  # Lazy initialization
except ImportError:
    EASYOCR_AVAILABLE = False
    print("⚠️  easyocr not available, using pytesseract only")


class OCRProcessor:
    """Handles OCR with pytesseract (primary) and easyocr (fallback)."""
    
    @staticmethod
    def preprocess_image(image: Image.Image) -> np.ndarray:
        """
        Preprocess image for better OCR accuracy.
        
        Steps:
        1. Convert to grayscale
        2. Resize if too small
        3. Increase contrast
        4. Denoise
        
        Args:
            image: PIL Image
        
        Returns:
            Preprocessed image as numpy array
        """
        # Convert PIL to OpenCV format
        img = np.array(image)
        
        # Convert to grayscale if not already
        if len(img.shape) == 3:
            img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        
        # Resize if image is too small (min 300px width for good OCR)
        height, width = img.shape
        if width < 300:
            scale = 300 / width
            new_width = int(width * scale)
            new_height = int(height * scale)
            img = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
        
        # Increase contrast using CLAHE
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        img = clahe.apply(img)
        
        # Denoise
        img = cv2.fastNlMeansDenoising(img, h=10)
        
        # Binarization (Otsu's method)
        _, img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        return img
    
    @staticmethod
    def ocr_pytesseract(image: Image.Image) -> tuple:
        """
        Extract text using Tesseract OCR.
        
        Args:
            image: PIL Image
        
        Returns:
            Tuple of (text, confidence)
        """
        try:
            # Preprocess image
            processed_img = OCRProcessor.preprocess_image(image)
            
            # Convert back to PIL for pytesseract
            pil_img = Image.fromarray(processed_img)
            
            # Extract text with confidence data
            data = pytesseract.image_to_data(pil_img, output_type=pytesseract.Output.DICT)
            
            # Calculate average confidence (filter out -1 values)
            confidences = [int(conf) for conf in data['conf'] if int(conf) != -1]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            # Extract text
            text = pytesseract.image_to_string(pil_img, config='--psm 6')
            
            return text, avg_confidence
        except Exception as e:
            print(f"   ⚠️  Tesseract OCR error: {e}")
            return "", 0
    
    @staticmethod
    def ocr_easyocr(image: Image.Image) -> str:
        """
        Extract text using EasyOCR (fallback).
        
        Args:
            image: PIL Image
        
        Returns:
            Extracted text
        """
        global _easyocr_reader
        
        if not EASYOCR_AVAILABLE:
            return ""
        
        try:
            # Lazy initialization of EasyOCR reader
            if _easyocr_reader is None:
                _easyocr_reader = easyocr.Reader(['en'], gpu=False)
            
            # Convert PIL to numpy array
            img = np.array(image)
            
            # EasyOCR expects RGB
            if len(img.shape) == 2:
                img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
            
            # Extract text
            results = _easyocr_reader.readtext(img, detail=0)
            text = ' '.join(results)
            
            return text
        except Exception as e:
            print(f"   ⚠️  EasyOCR error: {e}")
            return ""
    
    @staticmethod
    def ocr_image(image: Image.Image, confidence_threshold: float = 60.0) -> str:
        """
        Main OCR function with fallback logic.
        
        Strategy:
        1. Try pytesseract first
        2. If confidence < threshold, try easyocr
        3. Return best result
        
        Args:
            image: PIL Image
            confidence_threshold: Minimum confidence for pytesseract (default 60%)
        
        Returns:
            Extracted text
        """
        # Try pytesseract first
        text_tesseract, confidence = OCRProcessor.ocr_pytesseract(image)
        
        # If confidence is good, use pytesseract result
        if confidence >= confidence_threshold:
            return text_tesseract
        
        # Low confidence - try easyocr as fallback
        if EASYOCR_AVAILABLE and confidence < confidence_threshold:
            print(f"   ⚠️  Low confidence ({confidence:.1f}%), trying EasyOCR fallback...")
            text_easyocr = OCRProcessor.ocr_easyocr(image)
            
            # Use easyocr result if it found more text
            if len(text_easyocr) > len(text_tesseract):
                return text_easyocr
        
        # Return pytesseract result (even if low confidence)
        return text_tesseract


class ImageTransformer:
    """
    Image Transformer for loading and processing images (PNG/JPG).
    Handles preprocessing and OCR text extraction.
    """
    
    def __init__(self):
        """Initialize the image transformer."""
        self.ocr_processor = OCRProcessor()
    
    def load_image(self, image_path: Path) -> List[Dict]:
        """
        Load and process image file (PNG/JPG).
        
        Args:
            image_path: Path to image file
        
        Returns:
            List with single dictionary containing extracted text and metadata
        """
        print(f"🖼️  Processing: {image_path.name}")
        
        try:
            # Open image
            img = Image.open(image_path)
            
            # Convert to RGB if needed (some PNGs have alpha channel)
            if img.mode not in ('RGB', 'L'):
                img = img.convert('RGB')
            
            # Extract text using OCR
            text = self.ocr_processor.ocr_image(img)
            
            if text and text.strip():
                result = {
                    'id': str(uuid.uuid4()),
                    'source': image_path.name,
                    'page': 1,  # Images are single-page
                    'modality': 'image',
                    'extraction_method': 'ocr',
                    'text': text
                }
                
                print(f"   ✅ Extracted text ({len(text)} characters)")
                return [result]
            else:
                print(f"   ⚠️  No text found in image")
                return []
        
        except Exception as e:
            print(f"   ❌ Error processing image: {e}")
            return []
    
    def load_images_batch(self, image_dir: Path) -> List[Dict]:
        """
        Load all images from a directory.
        
        Args:
            image_dir: Directory containing image files
        
        Returns:
            List of extraction results
        """
        results = []
        
        # Get all image files
        image_files = []
        if image_dir.exists():
            image_files.extend(image_dir.glob('*.png'))
            image_files.extend(image_dir.glob('*.PNG'))
            image_files.extend(image_dir.glob('*.jpg'))
            image_files.extend(image_dir.glob('*.JPG'))
            image_files.extend(image_dir.glob('*.jpeg'))
            image_files.extend(image_dir.glob('*.JPEG'))
        
        print(f"\n📸 Found {len(image_files)} image(s) in {image_dir.name}")
        
        for img_path in sorted(image_files):
            result = self.load_image(img_path)
            results.extend(result)
        
        return results
    
    def transform(self, image_input) -> List[Dict]:
        """
        Main transformation method. Accepts Path or directory.
        
        Args:
            image_input: Path to image file or directory
        
        Returns:
            List of extraction results
        """
        if isinstance(image_input, str):
            image_input = Path(image_input)
        
        if image_input.is_file():
            return self.load_image(image_input)
        elif image_input.is_dir():
            return self.load_images_batch(image_input)
        else:
            print(f"❌ Invalid input: {image_input}")
            return []
