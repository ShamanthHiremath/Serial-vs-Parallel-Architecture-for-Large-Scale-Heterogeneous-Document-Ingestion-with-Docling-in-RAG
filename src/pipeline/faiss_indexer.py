"""FAISS indexing module for vector storage and retrieval."""

import faiss
import numpy as np
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class FAISSIndexer:
    """Manage FAISS index for document embeddings."""
    
    def __init__(self, dimension: int, index_type: str = 'flat'):
        """
        Initialize FAISS indexer.
        
        Args:
            dimension: Dimension of embeddings
            index_type: Type of FAISS index ('flat', 'ivf', 'hnsw')
        """
        self.dimension = dimension
        self.index_type = index_type
        self.index = None
        self.document_metadata = []
        self._initialize_index()
    
    def _initialize_index(self):
        """Initialize FAISS index."""
        try:
            if self.index_type == 'flat':
                # L2 distance for cosine similarity with normalized vectors
                self.index = faiss.IndexFlatL2(self.dimension)
            elif self.index_type == 'ivf':
                # IVF index for larger datasets
                quantizer = faiss.IndexFlatL2(self.dimension)
                self.index = faiss.IndexIVFFlat(quantizer, self.dimension, 100)
            elif self.index_type == 'hnsw':
                # HNSW index for fast approximate search
                self.index = faiss.IndexHNSWFlat(self.dimension, 32)
            else:
                raise ValueError(f"Unknown index type: {self.index_type}")
            
            logger.info(f"FAISS index initialized: {self.index_type}, dimension: {self.dimension}")
        except Exception as e:
            logger.error(f"Failed to initialize FAISS index: {e}")
            raise
    
    def add_documents(self, documents: List[Dict[str, Any]]) -> int:
        """
        Add documents to the index.
        
        Args:
            documents: List of document dictionaries with embeddings
            
        Returns:
            Number of documents added
        """
        if self.index is None:
            raise RuntimeError("FAISS index not initialized")
        
        embeddings = []
        valid_docs = []
        
        for doc in documents:
            if doc.get('embedding') is not None:
                embeddings.append(doc['embedding'])
                valid_docs.append({
                    'file_path': doc.get('file_path'),
                    'file_name': doc.get('file_name'),
                    'file_type': doc.get('file_type')
                })
        
        if not embeddings:
            logger.warning("No valid embeddings to add to index")
            return 0
        
        try:
            # Convert to numpy array and normalize
            embeddings_array = np.array(embeddings).astype('float32')
            
            # Normalize vectors for cosine similarity
            faiss.normalize_L2(embeddings_array)
            
            # Train index if needed (for IVF)
            if self.index_type == 'ivf' and not self.index.is_trained:
                logger.info("Training IVF index...")
                self.index.train(embeddings_array)
            
            # Add to index
            self.index.add(embeddings_array)
            self.document_metadata.extend(valid_docs)
            
            logger.info(f"Added {len(embeddings)} documents to FAISS index. Total: {self.index.ntotal}")
            return len(embeddings)
        except Exception as e:
            logger.error(f"Error adding documents to FAISS index: {e}")
            raise
    
    def search(self, query_embedding: np.ndarray, k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for similar documents.
        
        Args:
            query_embedding: Query embedding vector
            k: Number of results to return
            
        Returns:
            List of search results with metadata
        """
        if self.index is None or self.index.ntotal == 0:
            logger.warning("Index is empty or not initialized")
            return []
        
        try:
            # Normalize query
            query = np.array([query_embedding]).astype('float32')
            faiss.normalize_L2(query)
            
            # Search
            distances, indices = self.index.search(query, k)
            
            # Prepare results
            results = []
            for dist, idx in zip(distances[0], indices[0]):
                if idx >= 0 and idx < len(self.document_metadata):
                    result = self.document_metadata[idx].copy()
                    result['distance'] = float(dist)
                    result['similarity'] = 1.0 - float(dist)  # Convert L2 to similarity
                    results.append(result)
            
            return results
        except Exception as e:
            logger.error(f"Error searching FAISS index: {e}")
            raise
    
    def get_stats(self) -> Dict[str, Any]:
        """Get index statistics."""
        return {
            'total_documents': self.index.ntotal if self.index else 0,
            'dimension': self.dimension,
            'index_type': self.index_type,
            'is_trained': self.index.is_trained if hasattr(self.index, 'is_trained') else True
        }
