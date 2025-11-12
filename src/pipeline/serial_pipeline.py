"""Serial document processing pipeline."""

import time
import logging
from typing import List, Dict, Any
from tqdm import tqdm

from .document_loader import DocumentLoader
from .ocr_processor import OCRProcessor
from .embedding_processor import EmbeddingProcessor
from .faiss_indexer import FAISSIndexer
from ..utils.metrics import MetricsCollector

logger = logging.getLogger(__name__)


class SerialPipeline:
    """Process documents sequentially in serial mode."""
    
    def __init__(self, device: str = 'cpu', embedding_model: str = 'all-MiniLM-L6-v2'):
        """
        Initialize serial pipeline.
        
        Args:
            device: 'cpu' or 'cuda' for GPU acceleration
            embedding_model: Name of sentence-transformer model
        """
        self.device = device
        self.embedding_model = embedding_model
        
        # Initialize components
        self.loader = DocumentLoader()
        self.ocr = OCRProcessor(device=device)
        self.embedder = EmbeddingProcessor(model_name=embedding_model, device=device)
        
        # Initialize FAISS index
        embedding_dim = self.embedder.get_embedding_dimension()
        self.indexer = FAISSIndexer(dimension=embedding_dim, index_type='flat')
        
        # Metrics collector
        self.metrics = MetricsCollector()
        
        logger.info(f"Serial pipeline initialized with device: {device}")
    
    def process_corpus(self, corpus_path: str) -> Dict[str, Any]:
        """
        Process all documents in corpus serially.
        
        Args:
            corpus_path: Path to document corpus
            
        Returns:
            Processing results and metrics
        """
        logger.info(f"Starting serial processing of corpus: {corpus_path}")
        
        # Find documents
        document_paths = self.loader.find_documents(corpus_path)
        logger.info(f"Found {len(document_paths)} documents")
        
        if not document_paths:
            logger.warning("No documents found in corpus")
            return {'error': 'No documents found'}
        
        # Start metrics collection
        self.metrics.start_timing()
        
        # Process each document sequentially
        processed_docs = []
        for doc_path in tqdm(document_paths, desc="Processing documents"):
            doc_info = self._process_single_document(doc_path)
            if doc_info:
                processed_docs.append(doc_info)
            
            # Record system metrics periodically
            self.metrics.record_system_metrics()
        
        # Add all processed documents to FAISS index
        if processed_docs:
            self.indexer.add_documents(processed_docs)
        
        # End metrics collection
        self.metrics.end_timing()
        
        # Calculate statistics
        stats = self.metrics.calculate_statistics()
        stats['mode'] = 'serial'
        stats['corpus_path'] = corpus_path
        stats['device'] = self.device
        stats['embedding_model'] = self.embedding_model
        
        # Add index stats
        index_stats = self.indexer.get_stats()
        stats.update({f'index_{k}': v for k, v in index_stats.items()})
        
        logger.info(f"Serial processing completed. Processed {stats['num_documents']} documents in {stats['total_time_seconds']:.2f}s")
        
        return stats
    
    def _process_single_document(self, doc_path: str) -> Dict[str, Any]:
        """
        Process a single document through the pipeline.
        
        Args:
            doc_path: Path to document
            
        Returns:
            Processed document information
        """
        start_time = time.time()
        
        try:
            # Load document
            doc_info = self.loader.load_document(doc_path)
            
            # Apply OCR if needed
            if doc_info.get('requires_ocr', False):
                doc_info = self.ocr.process_document(doc_info)
            
            # Generate embeddings
            doc_info = self.embedder.process_document(doc_info)
            
            # Record metrics
            duration = time.time() - start_time
            self.metrics.record_document_processing(doc_info, duration)
            
            return doc_info
            
        except Exception as e:
            logger.error(f"Error processing document {doc_path}: {e}")
            duration = time.time() - start_time
            error_info = {
                'file_path': doc_path,
                'error': str(e),
                'file_size': 0
            }
            self.metrics.record_document_processing(error_info, duration)
            return None
