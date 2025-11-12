<!-- # Migration to Docling

This document explains the changes made to use Docling as the primary document processing library.

## What Changed

### Previous Implementation
The pipeline previously used separate libraries for each document type:
- **PyPDF2** for PDF files
- **python-docx** for Word documents
- **python-pptx** for PowerPoint presentations
- **PIL** for image validation
- **EasyOCR** for all OCR processing

### New Implementation (Docling-based)
The pipeline now uses **Docling** as the unified document processing library:
- **Docling** handles PDF, DOCX, PPTX, HTML, Markdown, and images
- Built-in OCR capabilities through Docling
- **EasyOCR** as supplementary OCR for enhanced accuracy
- **PIL** for image validation

## Benefits of Docling

1. **Unified API**: Single library handles multiple document formats
2. **Better Quality**: Docling provides higher quality text extraction
3. **Built-in OCR**: Integrated OCR for scanned documents and images
4. **Table Extraction**: Advanced table structure recognition
5. **Layout Preservation**: Better understanding of document structure
6. **Active Development**: Regularly updated and maintained

## Code Changes

### Document Loader (`src/pipeline/document_loader.py`)

**Before:**
```python
from docx import Document as DocxDocument
import PyPDF2
from pptx import Presentation

# Separate methods for each format
def _load_pdf(self, file_path: Path, doc_info: Dict) -> Dict:
    with open(file_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        # Extract text...

def _load_docx(self, file_path: Path, doc_info: Dict) -> Dict:
    document = DocxDocument(file_path)
    # Extract text...
```

**After:**
```python
from docling.document_converter import DocumentConverter
from docling.datamodel.pipeline_options import PipelineOptions

# Unified processing through Docling
def load_document(self, file_path: str) -> Dict[str, Any]:
    result = self.converter.convert(str(file_path))
    doc_info['text'] = result.document.export_to_markdown()
    # All formats handled automatically
```

### Requirements (`requirements.txt`)

**Removed:**
- python-docx
- PyPDF2
- python-pptx

**Added:**
- docling
- docling-core

**Kept:**
- easyocr (for supplementary OCR)
- pillow (for image validation)
- All embedding and indexing libraries

## Supported Formats

Docling now handles:
- ✅ PDF (text-based and scanned)
- ✅ DOCX (Microsoft Word)
- ✅ PPTX (PowerPoint)
- ✅ HTML
- ✅ Markdown (.md)
- ✅ Images (JPG, PNG, BMP, TIFF)

## Breaking Changes

### 1. File Format Support
**New formats added:**
- HTML files (.html)
- Markdown files (.md)

These were not supported in the previous version.

### 2. Text Extraction Format
Docling exports text in **Markdown format**, which:
- Preserves document structure better
- Includes formatting information
- May differ slightly from plain text extraction

### 3. OCR Behavior
- Docling has built-in OCR that runs automatically for scanned documents
- EasyOCR is now supplementary (can be disabled if not needed)
- OCR quality may improve due to Docling's optimizations

## Migration Steps

If you have custom code using the old implementation:

### 1. Update Dependencies
```bash
pip install --upgrade -r requirements.txt
```

### 2. Update Document Processing Code
If you were directly using the DocumentLoader:

**Before:**
```python
loader = DocumentLoader()
doc_info = loader.load_document("file.pdf")
text = doc_info['text']  # Plain text
```

**After:**
```python
loader = DocumentLoader(use_ocr=True)  # Enable OCR
doc_info = loader.load_document("file.pdf")
text = doc_info['text']  # Markdown formatted text
```

### 3. Handle Markdown Output
If you need plain text instead of Markdown:

```python
import re

def markdown_to_plain_text(markdown_text):
    # Remove markdown formatting
    text = re.sub(r'#+\s', '', markdown_text)  # Headers
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)  # Bold
    text = re.sub(r'\*(.+?)\*', r'\1', text)  # Italic
    text = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', text)  # Links
    return text

plain_text = markdown_to_plain_text(doc_info['text'])
```

### 4. Test with Your Documents
Run a test with your document corpus:

```bash
python benchmark.py --corpus-path /path/to/test/docs --mode serial --verbose
```

Check the logs for any processing errors or warnings.

## Configuration Options

### Enable/Disable OCR
```python
# With OCR (default)
loader = DocumentLoader(use_ocr=True)

# Without OCR (faster, text-only PDFs)
loader = DocumentLoader(use_ocr=False)
```

### Pipeline Options
Docling's pipeline can be configured:

```python
from docling.datamodel.pipeline_options import PipelineOptions

options = PipelineOptions()
options.do_ocr = True  # Enable OCR
options.do_table_structure = True  # Extract table structure
```

## Troubleshooting

### Issue: "Docling not available"
**Solution:** Install docling: `pip install docling`

### Issue: Slower processing
**Solution:** Docling is more comprehensive. For speed, disable OCR: `DocumentLoader(use_ocr=False)`

### Issue: Different text output
**Solution:** Docling preserves structure better. Use markdown-to-plain-text conversion if needed.

### Issue: Memory usage increased
**Solution:** Docling loads models for better extraction. Reduce parallel workers if needed.

## Performance Impact

### Pros:
- Better text quality
- Built-in OCR
- Support for more formats
- Better table extraction

### Cons:
- Slightly higher memory usage
- Initial model loading time
- Text in Markdown format (may need conversion)

## Rollback (if needed)

If you need to rollback to the old implementation:

1. Restore previous `requirements.txt` (from git history)
2. Restore previous `document_loader.py` (from git history)
3. Run: `pip install -r requirements.txt`

However, we recommend using Docling for better quality and maintainability.

## Further Reading

- [Docling Documentation](https://github.com/DS4SD/docling)
- [Docling Paper](https://arxiv.org/abs/2408.09869)
- [Docling Examples](https://github.com/DS4SD/docling/tree/main/examples)

## Support

For issues related to:
- **Docling library**: Check [Docling GitHub Issues](https://github.com/DS4SD/docling/issues)
- **Pipeline integration**: Open an issue in this repository
- **Migration help**: See CONTRIBUTING.md for guidelines -->
