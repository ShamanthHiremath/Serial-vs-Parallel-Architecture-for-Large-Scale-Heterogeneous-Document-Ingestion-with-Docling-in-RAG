"""OCR module using EasyOCR with GPU support."""

import easyocr
from typing import Dict, Any, Optional
import logging
from PIL import Image
import numpy as np

logger = logging.getLogger(__name__)


class OCRProcessor:
    """Process images and scanned documents with OCR."""
    
    def __init__(self, device: str = 'cpu', languages: list = None):
        """
        Initialize OCR processor.
        
        Args:
            device: 'cpu' or 'cuda' for GPU acceleration
            languages: List of language codes (default: ['en'])
        """
        self.device = device
        self.languages = languages or ['en']
        self.reader = None
        self._initialize_reader()
    
    def _initialize_reader(self):
        """Initialize EasyOCR reader."""
        try:
            use_gpu = self.device == 'cuda'
            logger.info(f"Initializing EasyOCR with device: {self.device}, GPU: {use_gpu}")
            self.reader = easyocr.Reader(
                self.languages,
                gpu=use_gpu,
                verbose=False
            )
            logger.info("EasyOCR initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize EasyOCR: {e}")
            raise
    
    def process_document(self, doc_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process document with OCR if needed.
        
        Args:
            doc_info: Document information dictionary
            
        Returns:
            Updated document info with OCR text
        """
        if not doc_info.get('requires_ocr', False):
            return doc_info
        
        if not doc_info.get('image_path'):
            logger.warning(f"Document requires OCR but no image path provided: {doc_info.get('file_name')}")
            return doc_info
        
        try:
            text = self.extract_text(doc_info['image_path'])
            doc_info['text'] = text
            doc_info['ocr_performed'] = True
        except Exception as e:
            logger.error(f"OCR failed for {doc_info['file_name']}: {e}")
            doc_info['ocr_error'] = str(e)
        
        return doc_info
    
    def extract_text(self, image_path: str) -> str:
        """
        Extract text from an image using OCR.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Extracted text
        """
        if self.reader is None:
            raise RuntimeError("OCR reader not initialized")
        
        try:
            # Read image
            img = Image.open(image_path)
            img_array = np.array(img)
            
            # Perform OCR
            results = self.reader.readtext(img_array)
            
            # Extract text from results
            text_parts = [detection[1] for detection in results]
            text = ' '.join(text_parts)
            
            return text
        except Exception as e:
            logger.error(f"Error extracting text from {image_path}: {e}")
            raise
