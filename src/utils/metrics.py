"""Metrics collection module for benchmarking."""

import time
import psutil
import logging
from typing import List, Dict, Any, Optional
import numpy as np
from collections import defaultdict

logger = logging.getLogger(__name__)

# Try to import GPU monitoring libraries
try:
    import GPUtil
    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False
    logger.warning("GPUtil not available. GPU metrics will not be collected.")


class MetricsCollector:
    """Collect performance metrics during pipeline execution."""
    
    def __init__(self):
        """Initialize metrics collector."""
        self.metrics = defaultdict(list)
        self.start_time = None
        self.end_time = None
        self.process = psutil.Process()
        self.gpu_available = GPU_AVAILABLE
    
    def start_timing(self):
        """Start overall timing."""
        self.start_time = time.time()
        logger.info("Metrics collection started")
    
    def end_timing(self):
        """End overall timing."""
        self.end_time = time.time()
        logger.info("Metrics collection ended")
    
    def record_document_processing(self, doc_info: Dict[str, Any], duration: float):
        """
        Record metrics for a single document processing.
        
        Args:
            doc_info: Document information
            duration: Processing time in seconds
        """
        self.metrics['document_latencies'].append(duration)
        self.metrics['document_sizes'].append(doc_info.get('file_size', 0))
        self.metrics['document_types'].append(doc_info.get('file_type', 'unknown'))
    
    def record_system_metrics(self):
        """Record current system resource usage."""
        try:
            # CPU metrics
            cpu_percent = self.process.cpu_percent(interval=0.1)
            self.metrics['cpu_usage'].append(cpu_percent)
            
            # Memory metrics
            memory_info = self.process.memory_info()
            memory_mb = memory_info.rss / 1024 / 1024
            self.metrics['memory_usage_mb'].append(memory_mb)
            
            # GPU metrics
            if self.gpu_available:
                try:
                    gpus = GPUtil.getGPUs()
                    if gpus:
                        for gpu in gpus:
                            self.metrics[f'gpu_{gpu.id}_usage'].append(gpu.load * 100)
                            self.metrics[f'gpu_{gpu.id}_memory_mb'].append(gpu.memoryUsed)
                except Exception as e:
                    logger.debug(f"Error collecting GPU metrics: {e}")
        except Exception as e:
            logger.warning(f"Error recording system metrics: {e}")
    
    def calculate_statistics(self) -> Dict[str, Any]:
        """
        Calculate final statistics from collected metrics.
        
        Returns:
            Dictionary of calculated statistics
        """
        stats = {}
        
        # Overall timing
        if self.start_time and self.end_time:
            total_time = self.end_time - self.start_time
            stats['total_time_seconds'] = total_time
        else:
            stats['total_time_seconds'] = 0
        
        # Document processing stats
        latencies = self.metrics.get('document_latencies', [])
        if latencies:
            stats['num_documents'] = len(latencies)
            stats['throughput_docs_per_sec'] = len(latencies) / stats['total_time_seconds'] if stats['total_time_seconds'] > 0 else 0
            stats['latency_mean_sec'] = np.mean(latencies)
            stats['latency_median_sec'] = np.median(latencies)
            stats['latency_p50_sec'] = np.percentile(latencies, 50)
            stats['latency_p95_sec'] = np.percentile(latencies, 95)
            stats['latency_p99_sec'] = np.percentile(latencies, 99)
            stats['latency_min_sec'] = np.min(latencies)
            stats['latency_max_sec'] = np.max(latencies)
        else:
            stats['num_documents'] = 0
            stats['throughput_docs_per_sec'] = 0
        
        # System resource stats
        for metric_name in ['cpu_usage', 'memory_usage_mb']:
            values = self.metrics.get(metric_name, [])
            if values:
                stats[f'{metric_name}_mean'] = np.mean(values)
                stats[f'{metric_name}_max'] = np.max(values)
                stats[f'{metric_name}_min'] = np.min(values)
        
        # GPU stats
        if self.gpu_available:
            for key in self.metrics.keys():
                if key.startswith('gpu_'):
                    values = self.metrics[key]
                    if values:
                        stats[f'{key}_mean'] = np.mean(values)
                        stats[f'{key}_max'] = np.max(values)
        
        # Document type distribution
        doc_types = self.metrics.get('document_types', [])
        if doc_types:
            type_counts = defaultdict(int)
            for doc_type in doc_types:
                type_counts[doc_type] += 1
            stats['document_type_distribution'] = dict(type_counts)
        
        # Total data processed
        sizes = self.metrics.get('document_sizes', [])
        if sizes:
            stats['total_data_mb'] = sum(sizes) / 1024 / 1024
            stats['avg_document_size_mb'] = np.mean(sizes) / 1024 / 1024
        
        return stats
    
    def get_raw_metrics(self) -> Dict[str, List]:
        """Get raw collected metrics."""
        return dict(self.metrics)
