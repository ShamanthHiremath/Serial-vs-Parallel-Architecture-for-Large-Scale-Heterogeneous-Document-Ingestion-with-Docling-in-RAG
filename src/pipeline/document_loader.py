"""Document loader module using Docling for various file formats."""

import os
from pathlib import Path
from typing import List, Dict, Any
import logging

try:
    from docling.document_converter import DocumentConverter
    from docling.datamodel.base_models import InputFormat
    from docling.datamodel.pipeline_options import PipelineOptions
    DOCLING_AVAILABLE = True
except ImportError:
    DOCLING_AVAILABLE = False
    logging.warning("Docling not available. Install with: pip install docling")

from PIL import Image

logger = logging.getLogger(__name__)


class DocumentLoader:
    """Load and extract text from various document formats using Docling."""
    
    SUPPORTED_FORMATS = {'.pdf', '.docx', '.pptx', '.html', '.md', '.jpg', '.jpeg', '.png', '.bmp', '.tiff'}
    
    def __init__(self, use_ocr: bool = True):
        """
        Initialize the document loader with Docling.
        
        Args:
            use_ocr: Whether to enable OCR for scanned documents and images
        """
        self.use_ocr = use_ocr
        self.converter = None
        
        if DOCLING_AVAILABLE:
            self._initialize_converter()
        else:
            logger.error("Docling library not available. Please install: pip install docling")
    
    def _initialize_converter(self):
        """Initialize Docling DocumentConverter."""
        try:
            # Configure pipeline options
            pipeline_options = PipelineOptions()
            pipeline_options.do_ocr = self.use_ocr
            pipeline_options.do_table_structure = True
            
            # Initialize converter with options
            self.converter = DocumentConverter(
                pipeline_options=pipeline_options
            )
            logger.info("Docling DocumentConverter initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Docling converter: {e}")
            raise
    
    def load_document(self, file_path: str) -> Dict[str, Any]:
        """
        Load a document and extract its content using Docling.
        
        Args:
            file_path: Path to the document file
            
        Returns:
            Dictionary containing document metadata and content
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        extension = file_path.suffix.lower()
        
        if extension not in self.SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported file format: {extension}")
        
        doc_info = {
            'file_path': str(file_path),
            'file_name': file_path.name,
            'file_type': extension,
            'file_size': file_path.stat().st_size,
            'text': '',
            'requires_ocr': False,
            'image_path': None
        }
        
        if not DOCLING_AVAILABLE or self.converter is None:
            # Fallback: mark images for external OCR
            if extension in {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}:
                doc_info = self._load_image_fallback(file_path, doc_info)
            else:
                logger.error("Docling not available and file is not an image")
                doc_info['error'] = "Docling library required for this file type"
            return doc_info
        
        try:
            # Use Docling to convert the document
            result = self.converter.convert(str(file_path))
            
            # Extract text from Docling result
            doc_info['text'] = result.document.export_to_markdown()
            
            # Add metadata from Docling
            if hasattr(result.document, 'pages'):
                doc_info['page_count'] = len(result.document.pages)
            
            # Store additional Docling metadata
            doc_info['docling_metadata'] = {
                'source': str(file_path),
                'format': extension,
            }
            
            # Check if OCR was performed
            if extension in {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}:
                doc_info['requires_ocr'] = True
                doc_info['ocr_performed'] = True
            elif extension == '.pdf' and not doc_info['text'].strip():
                # Scanned PDF that might need OCR
                doc_info['requires_ocr'] = True
                doc_info['image_path'] = str(file_path)
            
        except Exception as e:
            logger.error(f"Error loading document with Docling {file_path}: {e}")
            doc_info['error'] = str(e)
            
            # For images, fallback to marking for external OCR
            if extension in {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}:
                doc_info = self._load_image_fallback(file_path, doc_info)
        
        return doc_info
    
    def _load_image_fallback(self, file_path: Path, doc_info: Dict) -> Dict:
        """Fallback method to handle images when Docling OCR is not available."""
        try:
            img = Image.open(file_path)
            doc_info['image_size'] = img.size
            doc_info['image_mode'] = img.mode
            img.close()
        except Exception as e:
            raise ValueError(f"Invalid image file: {e}")
        
        doc_info['requires_ocr'] = True
        doc_info['image_path'] = str(file_path)
        return doc_info
    
    def find_documents(self, corpus_path: str) -> List[str]:
        """
        Find all supported documents in a directory.
        
        Args:
            corpus_path: Path to directory containing documents
            
        Returns:
            List of file paths
        """
        corpus_path = Path(corpus_path)
        
        if not corpus_path.exists():
            raise FileNotFoundError(f"Corpus path not found: {corpus_path}")
        
        if corpus_path.is_file():
            return [str(corpus_path)]
        
        documents = []
        for ext in self.SUPPORTED_FORMATS:
            documents.extend(corpus_path.rglob(f'*{ext}'))
        
        return [str(doc) for doc in sorted(documents)]
    
    def find_documents(self, corpus_path: str) -> List[str]:
        """
        Find all supported documents in a directory.
        
        Args:
            corpus_path: Path to directory containing documents
            
        Returns:
            List of file paths
        """
        corpus_path = Path(corpus_path)
        
        if not corpus_path.exists():
            raise FileNotFoundError(f"Corpus path not found: {corpus_path}")
        
        if corpus_path.is_file():
            return [str(corpus_path)]
        
        documents = []
        for ext in self.SUPPORTED_FORMATS:
            documents.extend(corpus_path.rglob(f'*{ext}'))
        
        return [str(doc) for doc in sorted(documents)]
