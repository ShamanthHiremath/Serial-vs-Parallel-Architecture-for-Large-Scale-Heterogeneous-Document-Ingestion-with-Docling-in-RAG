# Docling Integration Summary

## Overview

This pipeline now uses **Docling** as the primary document processing library, providing a unified, high-quality approach to document ingestion across multiple formats.

## What is Docling?

Docling is a powerful document processing library developed by IBM Research that provides:
- **Unified API** for multiple document formats
- **Built-in OCR** for scanned documents and images
- **Layout preservation** and structure understanding
- **Table extraction** with structure recognition
- **High-quality text extraction** with formatting
- **Export to multiple formats** (Markdown, JSON, etc.)

## Integration Details

### Document Formats Supported

Docling handles all document processing through a single `DocumentConverter`:

| Format | Extension | OCR Support | Notes |
|--------|-----------|-------------|-------|
| PDF | .pdf | ✅ | Text-based and scanned PDFs |
| Word | .docx | N/A | Native processing |
| PowerPoint | .pptx | N/A | Native processing |
| HTML | .html | N/A | Web pages and HTML docs |
| Markdown | .md | N/A | Markdown files |
| Images | .jpg, .png, .bmp, .tiff | ✅ | OCR extraction |

### How It Works

```python
from docling.document_converter import DocumentConverter
from docling.datamodel.pipeline_options import PipelineOptions

# Configure pipeline
pipeline_options = PipelineOptions()
pipeline_options.do_ocr = True  # Enable OCR
pipeline_options.do_table_structure = True  # Extract tables

# Create converter
converter = DocumentConverter(pipeline_options=pipeline_options)

# Convert document
result = converter.convert("document.pdf")

# Extract text in Markdown format
text = result.document.export_to_markdown()
```

### Pipeline Integration

The `DocumentLoader` class now uses Docling:

```python
class DocumentLoader:
    def __init__(self, use_ocr: bool = True):
        # Initialize Docling converter
        pipeline_options = PipelineOptions()
        pipeline_options.do_ocr = use_ocr
        pipeline_options.do_table_structure = True
        
        self.converter = DocumentConverter(
            pipeline_options=pipeline_options
        )
    
    def load_document(self, file_path: str) -> Dict[str, Any]:
        # Use Docling to process any supported format
        result = self.converter.convert(str(file_path))
        
        # Extract text (in Markdown format)
        text = result.document.export_to_markdown()
        
        return {
            'file_path': str(file_path),
            'text': text,
            'page_count': len(result.document.pages),
            # ... more metadata
        }
```

## Key Features

### 1. Unified Processing
**Before:** Different libraries for each format (PyPDF2, python-docx, python-pptx)  
**After:** Single Docling library handles all formats

### 2. Built-in OCR
**Before:** Separate OCR step with EasyOCR for all scanned content  
**After:** Docling includes OCR, EasyOCR is supplementary

### 3. Markdown Output
**Before:** Plain text extraction  
**After:** Markdown format preserving structure (headers, lists, tables)

### 4. Table Extraction
**Before:** Basic text extraction from tables  
**After:** Structured table recognition and extraction

### 5. Layout Understanding
**Before:** Sequential text extraction  
**After:** Document layout analysis and semantic understanding

## Configuration Options

### Enable/Disable OCR

```python
# With OCR (default) - for scanned documents
loader = DocumentLoader(use_ocr=True)

# Without OCR - faster, for text-only documents
loader = DocumentLoader(use_ocr=False)
```

### Pipeline Options

```python
from docling.datamodel.pipeline_options import PipelineOptions

options = PipelineOptions()
options.do_ocr = True              # Enable OCR
options.do_table_structure = True  # Extract table structure
options.images_scale = 2.0         # Image scaling for OCR
options.generate_page_images = False  # Don't generate page images
```

## Performance Considerations

### Advantages
- ✅ Better text quality
- ✅ Proper structure preservation
- ✅ Built-in OCR reduces external dependencies
- ✅ Single library = simpler codebase
- ✅ Support for more formats (HTML, Markdown)

### Trade-offs
- ⚠️ Slightly higher memory usage (model loading)
- ⚠️ Initial conversion may be slower (better quality)
- ⚠️ Output in Markdown format (may need conversion to plain text)

### Optimization Tips

1. **Disable OCR for text-only documents:**
   ```python
   loader = DocumentLoader(use_ocr=False)
   ```

2. **Adjust worker count for memory:**
   ```bash
   python benchmark.py --num-workers 2  # Reduce if memory constrained
   ```

3. **Use CPU for OCR if GPU unavailable:**
   ```bash
   python benchmark.py --device cpu
   ```

## Text Format: Markdown

Docling exports text in Markdown format, which preserves document structure:

### Example Output

```markdown
# Document Title

This is a paragraph with **bold** and *italic* text.

## Section Header

- Bullet point 1
- Bullet point 2

| Column 1 | Column 2 |
|----------|----------|
| Data 1   | Data 2   |
```

### Converting to Plain Text

If you need plain text instead of Markdown:

```python
import re

def markdown_to_plain_text(md_text):
    # Remove markdown syntax
    text = re.sub(r'#+\s', '', md_text)  # Headers
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)  # Bold
    text = re.sub(r'\*(.+?)\*', r'\1', text)  # Italic
    text = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', text)  # Links
    text = re.sub(r'\|', ' ', text)  # Table separators
    return text
```

## Fallback Behavior

If Docling is not installed:
- Images are marked for external OCR processing
- Other formats will raise an error
- Installation message is displayed

## Benefits for RAG Pipelines

1. **Better Context Preservation:** Markdown format retains document structure
2. **Table Understanding:** Structured table data improves Q&A accuracy
3. **Layout Awareness:** Section headers help with semantic chunking
4. **Multi-format Support:** Process diverse document types uniformly
5. **Quality Text Extraction:** Better OCR and text recognition

## Example: Complete Pipeline

```python
# Initialize with Docling
loader = DocumentLoader(use_ocr=True)

# Process a document
doc_info = loader.load_document("research_paper.pdf")

# Text is in Markdown format
print(doc_info['text'])
# Output:
# # Research Paper Title
# 
# ## Abstract
# This paper discusses...
# 
# ## Introduction
# ...

# Generate embeddings from the markdown text
embedder = EmbeddingProcessor()
doc_info = embedder.process_document(doc_info)

# Index in FAISS
indexer = FAISSIndexer(dimension=384)
indexer.add_documents([doc_info])
```

## Dependencies

Docling installation includes:
- Core document processing capabilities
- OCR models
- Layout analysis models
- Table detection models

Total size: ~500MB-1GB (depending on models)

## Resources

- **Docling GitHub:** https://github.com/DS4SD/docling
- **Docling Paper:** https://arxiv.org/abs/2408.09869
- **Documentation:** See Docling repository for detailed docs
- **Examples:** https://github.com/DS4SD/docling/tree/main/examples

## Support

For Docling-specific issues:
- Check [Docling GitHub Issues](https://github.com/DS4SD/docling/issues)
- Review [Docling Documentation](https://github.com/DS4SD/docling)

For pipeline integration issues:
- See MIGRATION.md for migration help
- Open an issue in this repository
- Check TROUBLESHOOTING section in README.md

## Summary

The integration of Docling provides:
- ✅ **Unified processing** for all document types
- ✅ **Higher quality** text extraction
- ✅ **Built-in OCR** capabilities
- ✅ **Structure preservation** via Markdown
- ✅ **Simplified codebase** with single library
- ✅ **Extended format support** (HTML, Markdown)
- ✅ **Better RAG performance** with improved context

This makes the pipeline more powerful, maintainable, and suitable for production RAG applications.
