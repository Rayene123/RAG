# Transformers - Document Processing for RAG

This folder contains transformers for processing multimodal documents (images and PDFs) and extracting text for the RAG pipeline.

## Available Transformers

### 1. ImageTransformer
Processes image files (PNG, JPG, JPEG) and extracts text using OCR.

**Features:**
- Automatic image preprocessing (grayscale, resizing, contrast enhancement, denoising)
- Dual OCR engine support: Tesseract (primary) + EasyOCR (fallback)
- Batch processing for multiple images
- Confidence-based fallback mechanism

### 2. PDFTransformer
Processes PDF files with automatic detection of text-based vs scanned PDFs.

**Features:**
- Automatic PDF type detection
- Direct text extraction for text-based PDFs (pdfplumber)
- OCR processing for scanned PDFs (converts to images then applies OCR)
- Batch processing for multiple PDFs

---

## Integration into RAG Pipeline

### Step 1: Import the Transformers

```python
from rag_core.query_processor.transformers.image_transformer import ImageTransformer
from rag_core.query_processor.transformers.pdf_transformer import PDFTransformer
```

### Step 2: Initialize Transformers

```python
# Initialize transformers
image_transformer = ImageTransformer()
pdf_transformer = PDFTransformer()
```

### Step 3: Process Documents

#### Single File Processing

```python
# Process a single image
results = image_transformer.transform("path/to/image.png")

# Process a single PDF
results = pdf_transformer.transform("path/to/document.pdf")

# Each result is a list of dictionaries:
# [
#   {
#     'id': 'unique-uuid',
#     'source': 'filename.png',
#     'page': 1,
#     'modality': 'image',  # or 'pdf'
#     'extraction_method': 'ocr',  # or 'direct'
#     'text': 'extracted text content...'
#   }
# ]
```

#### Batch Processing

```python
# Process all images in a directory
results = image_transformer.load_images_batch(Path("data/images"))

# Process all PDFs in a directory
results = pdf_transformer.load_pdfs_batch(Path("data/pdfs"))
```

### Step 4: Integrate with Your Ingestion Pipeline

**Example: Add to your ingestion script**

```python
from pathlib import Path
from rag_core.query_processor.transformers.image_transformer import ImageTransformer
from rag_core.query_processor.transformers.pdf_transformer import PDFTransformer
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

# Initialize components
image_transformer = ImageTransformer()
pdf_transformer = PDFTransformer()
embedder = SentenceTransformer('all-MiniLM-L6-v2')
qdrant_client = QdrantClient(url="http://localhost:6333")

# Process documents
def ingest_documents(data_dir: Path, collection_name: str):
    """Ingest images and PDFs into Qdrant."""
    
    all_documents = []
    
    # Process images
    image_dir = data_dir / "images"
    if image_dir.exists():
        print(f"Processing images from {image_dir}...")
        image_results = image_transformer.load_images_batch(image_dir)
        all_documents.extend(image_results)
    
    # Process PDFs
    pdf_dir = data_dir / "pdfs"
    if pdf_dir.exists():
        print(f"Processing PDFs from {pdf_dir}...")
        pdf_results = pdf_transformer.load_pdfs_batch(pdf_dir)
        all_documents.extend(pdf_results)
    
    # Create embeddings and store in Qdrant
    for doc in all_documents:
        if doc['text'].strip():
            embedding = embedder.encode(doc['text']).tolist()
            
            qdrant_client.upsert(
                collection_name=collection_name,
                points=[{
                    "id": doc['id'],
                    "vector": embedding,
                    "payload": {
                        "text": doc['text'],
                        "source": doc['source'],
                        "page": doc['page'],
                        "modality": doc['modality'],
                        "extraction_method": doc['extraction_method']
                    }
                }]
            )
    
    print(f"✅ Ingested {len(all_documents)} documents into {collection_name}")

# Usage
ingest_documents(Path("data"), "my_collection")
```

### Step 5: Use in Query Processing

```python
from rag_core.query_processor.transformers.image_transformer import ImageTransformer

# When a user uploads an image as a query
image_transformer = ImageTransformer()
query_results = image_transformer.transform(uploaded_image_path)
query_text = query_results[0]['text']

# Use extracted text for similarity search
embedding = embedder.encode(query_text)
search_results = qdrant_client.search(
    collection_name="my_collection",
    query_vector=embedding,
    limit=5
)
```

---

## Output Format

All transformers return a list of dictionaries with the following structure:

```python
{
    'id': str,                    # Unique UUID for the document
    'source': str,                # Original filename
    'page': int,                  # Page number (1 for images)
    'modality': str,              # 'image' or 'pdf'
    'extraction_method': str,     # 'ocr' or 'direct'
    'text': str                   # Extracted text content
}
```

---

## Dependencies

Required packages (already in requirements.txt):
```
opencv-python>=4.8.0
pillow>=10.0.0
pytesseract>=0.3.10
pdfplumber>=0.10.0
PyMuPDF>=1.23.0
easyocr>=1.7.0  # Optional but recommended
```

**Important:** Tesseract OCR must be installed separately:
- Windows: https://github.com/UB-Mannheim/tesseract/wiki
- The transformers automatically detect Tesseract on Windows

---

## Example: Complete RAG Ingestion Script

```python
"""
Complete example: Ingest multimodal documents into RAG system
"""

from pathlib import Path
from rag_core.query_processor.transformers.image_transformer import ImageTransformer
from rag_core.query_processor.transformers.pdf_transformer import PDFTransformer

def extract_all_documents(data_dir: Path):
    """Extract text from all images and PDFs in data directory."""
    
    image_transformer = ImageTransformer()
    pdf_transformer = PDFTransformer()
    
    all_results = []
    
    # Process images
    image_dir = data_dir / "images"
    if image_dir.exists():
        print("\n📸 Processing Images...")
        results = image_transformer.load_images_batch(image_dir)
        all_results.extend(results)
        print(f"   Extracted {len(results)} image(s)")
    
    # Process PDFs
    pdf_dir = data_dir / "pdfs"
    if pdf_dir.exists():
        print("\n📄 Processing PDFs...")
        results = pdf_transformer.load_pdfs_batch(pdf_dir)
        all_results.extend(results)
        print(f"   Extracted {len(results)} page(s)")
    
    print(f"\n✅ Total: {len(all_results)} documents extracted")
    return all_results

if __name__ == "__main__":
    # Extract from your data directory
    documents = extract_all_documents(Path("data"))
    
    # Now use 'documents' for embedding and storing in Qdrant
    # ... your embedding and storage logic here ...
```

---

## Tips for Production

1. **Chunking:** For long documents, chunk the text before embedding
2. **Metadata:** Preserve source, page, and modality info for better retrieval
3. **Error Handling:** Some images/PDFs may fail - handle gracefully
4. **Batch Size:** For large datasets, process in batches to avoid memory issues
5. **Caching:** Cache processed documents to avoid re-processing

---

## Troubleshooting

**Issue:** Tesseract not found
- **Solution:** Install Tesseract OCR and ensure it's in your PATH

**Issue:** Low OCR accuracy
- **Solution:** Install EasyOCR as fallback: `pip install easyocr`

**Issue:** Large memory usage
- **Solution:** Process files in smaller batches using loops

**Issue:** PDF processing fails
- **Solution:** Check if PDF is encrypted or corrupted
