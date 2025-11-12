"""Parallel document processing pipeline."""

import time
import logging
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from tqdm import tqdm
import multiprocessing

from .document_loader import DocumentLoader
from .ocr_processor import OCRProcessor
from .embedding_processor import EmbeddingProcessor
from .faiss_indexer import FAISSIndexer
from ..utils.metrics import MetricsCollector

logger = logging.getLogger(__name__)


def process_document_worker(doc_path: str, device: str, embedding_model: str) -> Dict[str, Any]:
    """
    Worker function to process a single document (for multiprocessing).
    
    Args:
        doc_path: Path to document
        device: Device to use
        embedding_model: Embedding model name
        
    Returns:
        Processed document information with timing
    """
    start_time = time.time()
    
    try:
        # Initialize components (each worker needs its own instances)
        loader = DocumentLoader()
        ocr = OCRProcessor(device=device)
        embedder = EmbeddingProcessor(model_name=embedding_model, device=device)
        
        # Load document
        doc_info = loader.load_document(doc_path)
        
        # Apply OCR if needed
        if doc_info.get('requires_ocr', False):
            doc_info = ocr.process_document(doc_info)
        
        # Generate embeddings
        doc_info = embedder.process_document(doc_info)
        
        # Add timing information
        doc_info['processing_time'] = time.time() - start_time
        
        return doc_info
        
    except Exception as e:
        logger.error(f"Error processing document {doc_path}: {e}")
        return {
            'file_path': doc_path,
            'error': str(e),
            'file_size': 0,
            'processing_time': time.time() - start_time
        }


class ParallelPipeline:
    """Process documents in parallel using multiple workers."""
    
    def __init__(self, device: str = 'cpu', embedding_model: str = 'all-MiniLM-L6-v2', 
                 num_workers: int = None, use_threads: bool = False):
        """
        Initialize parallel pipeline.
        
        Args:
            device: 'cpu' or 'cuda' for GPU acceleration
            embedding_model: Name of sentence-transformer model
            num_workers: Number of parallel workers (default: CPU count)
            use_threads: Use threads instead of processes
        """
        self.device = device
        self.embedding_model = embedding_model
        self.num_workers = num_workers or max(1, multiprocessing.cpu_count() - 1)
        self.use_threads = use_threads
        
        # Initialize loader (for finding documents)
        self.loader = DocumentLoader()
        
        # Initialize embedding model to get dimension
        temp_embedder = EmbeddingProcessor(model_name=embedding_model, device=device)
        embedding_dim = temp_embedder.get_embedding_dimension()
        
        # Initialize FAISS index
        self.indexer = FAISSIndexer(dimension=embedding_dim, index_type='flat')
        
        # Metrics collector
        self.metrics = MetricsCollector()
        
        logger.info(f"Parallel pipeline initialized with {self.num_workers} workers, device: {device}")
    
    def process_corpus(self, corpus_path: str) -> Dict[str, Any]:
        """
        Process all documents in corpus in parallel.
        
        Args:
            corpus_path: Path to document corpus
            
        Returns:
            Processing results and metrics
        """
        logger.info(f"Starting parallel processing of corpus: {corpus_path}")
        
        # Find documents
        document_paths = self.loader.find_documents(corpus_path)
        logger.info(f"Found {len(document_paths)} documents")
        
        if not document_paths:
            logger.warning("No documents found in corpus")
            return {'error': 'No documents found'}
        
        # Start metrics collection
        self.metrics.start_timing()
        
        # Process documents in parallel
        processed_docs = []
        
        if self.use_threads:
            executor_class = ThreadPoolExecutor
        else:
            executor_class = ProcessPoolExecutor
        
        with executor_class(max_workers=self.num_workers) as executor:
            # Submit all tasks
            futures = {
                executor.submit(process_document_worker, doc_path, self.device, self.embedding_model): doc_path
                for doc_path in document_paths
            }
            
            # Process completed tasks with progress bar
            with tqdm(total=len(document_paths), desc="Processing documents") as pbar:
                for future in as_completed(futures):
                    doc_info = future.result()
                    
                    if doc_info and 'error' not in doc_info:
                        processed_docs.append(doc_info)
                        
                        # Record metrics
                        duration = doc_info.get('processing_time', 0)
                        self.metrics.record_document_processing(doc_info, duration)
                    
                    # Record system metrics
                    self.metrics.record_system_metrics()
                    
                    pbar.update(1)
        
        # Add all processed documents to FAISS index
        if processed_docs:
            self.indexer.add_documents(processed_docs)
        
        # End metrics collection
        self.metrics.end_timing()
        
        # Calculate statistics
        stats = self.metrics.calculate_statistics()
        stats['mode'] = 'parallel'
        stats['corpus_path'] = corpus_path
        stats['device'] = self.device
        stats['embedding_model'] = self.embedding_model
        stats['num_workers'] = self.num_workers
        stats['executor_type'] = 'threads' if self.use_threads else 'processes'
        
        # Add index stats
        index_stats = self.indexer.get_stats()
        stats.update({f'index_{k}': v for k, v in index_stats.items()})
        
        logger.info(f"Parallel processing completed. Processed {stats['num_documents']} documents in {stats['total_time_seconds']:.2f}s")
        
        return stats
