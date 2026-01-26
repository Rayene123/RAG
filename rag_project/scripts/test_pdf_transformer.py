"""
Test the PDF transformer with real client financial profile PDFs.
"""

import sys
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from rag_core.query_processor.transformers.pdf_transformer import PDFTransformer

def test_single_pdf(pdf_path):
    """Test transformer with a single PDF"""
    print("="*80)
    print(f"Testing PDF: {pdf_path.name}")
    print("="*80)
    
    # Initialize transformer
    transformer = PDFTransformer()
    
    # Process the PDF
    results = transformer.transform(str(pdf_path))
    
    if results:
        print(f"✅ Successfully extracted {len(results)} page(s)\n")
        
        # Show results for each page
        for i, result in enumerate(results, 1):
            print(f"--- Page {i} ---")
            print(f"Source: {result['source']}")
            print(f"Page Number: {result['page']}")
            print(f"Modality: {result['modality']}")
            print(f"Extraction Method: {result['extraction_method']}")
            print(f"Text Length: {len(result['text'])} characters")
            print(f"\nExtracted Text:\n")
            print("-"*80)
            print(result['text'])
            print("-"*80)
            print()
        
        return True
    else:
        print("❌ No text extracted from PDF")
        return False


def test_all_pdfs():
    """Test transformer with all PDFs in the raw folder"""
    pdf_dir = project_root / "embeddings" / "pdf" / "raw"
    
    if not pdf_dir.exists():
        print(f"❌ PDF directory not found: {pdf_dir}")
        return
    
    pdf_files = list(pdf_dir.glob("*.pdf"))
    
    if not pdf_files:
        print(f"❌ No PDF files found in {pdf_dir}")
        return
    
    print(f"\n{'='*80}")
    print(f"Found {len(pdf_files)} PDF file(s)")
    print(f"{'='*80}\n")
    
    for pdf_file in pdf_files:
        test_single_pdf(pdf_file)
        print("\n")


def main():
    """Main test function"""
    print("\n🔍 PDF TRANSFORMER TEST\n")
    
    # Test all PDFs
    test_all_pdfs()
    
    print("="*80)
    print("TEST COMPLETE")
    print("="*80)


if __name__ == "__main__":
    main()
