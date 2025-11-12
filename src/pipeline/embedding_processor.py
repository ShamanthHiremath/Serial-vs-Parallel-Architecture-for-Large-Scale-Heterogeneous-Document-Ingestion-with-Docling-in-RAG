"""Embedding module using sentence-transformers."""

from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any
import numpy as np
import logging

logger = logging.getLogger(__name__)


class EmbeddingProcessor:
    """Generate embeddings using sentence-transformers."""
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2', device: str = 'cpu'):
        """
        Initialize embedding processor.
        
        Args:
            model_name: Name of the sentence-transformer model
            device: 'cpu' or 'cuda' for GPU acceleration
        """
        self.model_name = model_name
        self.device = device
        self.model = None
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize sentence-transformer model."""
        try:
            logger.info(f"Loading sentence-transformer model: {self.model_name} on {self.device}")
            self.model = SentenceTransformer(self.model_name, device=self.device)
            logger.info(f"Model loaded successfully. Embedding dimension: {self.model.get_sentence_embedding_dimension()}")
        except Exception as e:
            logger.error(f"Failed to load sentence-transformer model: {e}")
            raise
    
    def process_document(self, doc_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate embeddings for document text.
        
        Args:
            doc_info: Document information dictionary
            
        Returns:
            Updated document info with embeddings
        """
        text = doc_info.get('text', '')
        
        if not text or not text.strip():
            logger.warning(f"No text available for embedding: {doc_info.get('file_name')}")
            doc_info['embedding'] = None
            return doc_info
        
        try:
            embedding = self.generate_embedding(text)
            doc_info['embedding'] = embedding
            doc_info['embedding_dim'] = len(embedding)
        except Exception as e:
            logger.error(f"Embedding generation failed for {doc_info['file_name']}: {e}")
            doc_info['embedding_error'] = str(e)
            doc_info['embedding'] = None
        
        return doc_info
    
    def generate_embedding(self, text: str) -> np.ndarray:
        """
        Generate embedding for text.
        
        Args:
            text: Input text
            
        Returns:
            Embedding vector as numpy array
        """
        if self.model is None:
            raise RuntimeError("Embedding model not initialized")
        
        # Truncate very long texts to avoid memory issues
        max_length = 512
        if len(text) > max_length * 10:  # Rough character estimate
            logger.warning(f"Text too long ({len(text)} chars), truncating")
            text = text[:max_length * 10]
        
        try:
            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings produced by the model."""
        if self.model is None:
            raise RuntimeError("Embedding model not initialized")
        return self.model.get_sentence_embedding_dimension()
