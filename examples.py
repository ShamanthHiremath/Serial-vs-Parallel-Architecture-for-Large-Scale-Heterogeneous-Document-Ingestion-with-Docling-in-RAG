#!/usr/bin/env python3
"""
Example script showing how to use the pipeline programmatically.
This demonstrates how to integrate the pipeline into your own code.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.pipeline.serial_pipeline import SerialPipeline
from src.pipeline.parallel_pipeline import ParallelPipeline
from src.utils.csv_output import CSVOutput


def example_serial_processing():
    """Example: Process documents using serial pipeline."""
    print("=" * 60)
    print("Example 1: Serial Processing")
    print("=" * 60)
    
    # Initialize serial pipeline
    pipeline = SerialPipeline(
        device='cpu',  # or 'cuda' for GPU
        embedding_model='all-MiniLM-L6-v2'
    )
    
    # Process corpus
    corpus_path = 'sample_corpus'  # Replace with your corpus path
    results = pipeline.process_corpus(corpus_path)
    
    # Print results
    print(f"\nProcessed {results.get('num_documents', 0)} documents")
    print(f"Throughput: {results.get('throughput_docs_per_sec', 0):.2f} docs/sec")
    print(f"Total time: {results.get('total_time_seconds', 0):.2f} seconds")
    
    return results


def example_parallel_processing():
    """Example: Process documents using parallel pipeline."""
    print("\n" + "=" * 60)
    print("Example 2: Parallel Processing")
    print("=" * 60)
    
    # Initialize parallel pipeline
    pipeline = ParallelPipeline(
        device='cpu',
        embedding_model='all-MiniLM-L6-v2',
        num_workers=4,  # Adjust based on your CPU cores
        use_threads=False  # Set to True for I/O-bound workloads
    )
    
    # Process corpus
    corpus_path = 'sample_corpus'
    results = pipeline.process_corpus(corpus_path)
    
    # Print results
    print(f"\nProcessed {results.get('num_documents', 0)} documents")
    print(f"Throughput: {results.get('throughput_docs_per_sec', 0):.2f} docs/sec")
    print(f"Total time: {results.get('total_time_seconds', 0):.2f} seconds")
    print(f"Workers used: {results.get('num_workers', 0)}")
    
    return results


def example_save_results():
    """Example: Save results to CSV."""
    print("\n" + "=" * 60)
    print("Example 3: Saving Results to CSV")
    print("=" * 60)
    
    # Run a quick benchmark
    pipeline = SerialPipeline(device='cpu')
    results = pipeline.process_corpus('sample_corpus')
    
    # Initialize CSV output
    csv_output = CSVOutput(output_dir='my_results')
    
    # Save results
    csv_file = csv_output.save_results(
        stats=results,
        mode='serial',
        run_id='example_run_001'
    )
    
    print(f"\nResults saved to: {csv_file}")
    
    # Also append to summary
    csv_output.append_results(stats=results, mode='serial')
    print("Results appended to summary file")


def example_custom_metrics():
    """Example: Access detailed metrics."""
    print("\n" + "=" * 60)
    print("Example 4: Accessing Detailed Metrics")
    print("=" * 60)
    
    pipeline = SerialPipeline(device='cpu')
    results = pipeline.process_corpus('sample_corpus')
    
    # Access specific metrics
    print("\nLatency Percentiles:")
    print(f"  P50: {results.get('latency_p50_sec', 0):.4f} sec")
    print(f"  P95: {results.get('latency_p95_sec', 0):.4f} sec")
    print(f"  P99: {results.get('latency_p99_sec', 0):.4f} sec")
    
    print("\nResource Usage:")
    print(f"  CPU (avg): {results.get('cpu_usage_mean', 0):.2f}%")
    print(f"  Memory (avg): {results.get('memory_usage_mb_mean', 0):.2f} MB")
    
    print("\nDocument Types:")
    doc_types = results.get('document_type_distribution', {})
    for doc_type, count in doc_types.items():
        print(f"  {doc_type}: {count} documents")


def example_compare_modes():
    """Example: Compare serial vs parallel performance."""
    print("\n" + "=" * 60)
    print("Example 5: Comparing Serial vs Parallel")
    print("=" * 60)
    
    corpus_path = 'sample_corpus'
    
    # Serial
    print("\nRunning serial mode...")
    serial_pipeline = SerialPipeline(device='cpu')
    serial_results = serial_pipeline.process_corpus(corpus_path)
    
    # Parallel
    print("\nRunning parallel mode...")
    parallel_pipeline = ParallelPipeline(device='cpu', num_workers=4)
    parallel_results = parallel_pipeline.process_corpus(corpus_path)
    
    # Compare
    print("\n" + "-" * 60)
    print("Comparison:")
    print("-" * 60)
    
    serial_time = serial_results.get('total_time_seconds', 1)
    parallel_time = parallel_results.get('total_time_seconds', 1)
    speedup = serial_time / parallel_time
    
    print(f"Serial time:    {serial_time:.2f} seconds")
    print(f"Parallel time:  {parallel_time:.2f} seconds")
    print(f"Speedup:        {speedup:.2f}x")
    
    serial_throughput = serial_results.get('throughput_docs_per_sec', 0)
    parallel_throughput = parallel_results.get('throughput_docs_per_sec', 0)
    
    print(f"\nSerial throughput:   {serial_throughput:.2f} docs/sec")
    print(f"Parallel throughput: {parallel_throughput:.2f} docs/sec")
    print(f"Improvement:         {(parallel_throughput/serial_throughput - 1)*100:.1f}%")


def main():
    """Run all examples."""
    print("\n" + "=" * 60)
    print("Document Ingestion Pipeline - Usage Examples")
    print("=" * 60)
    print("\nNote: Make sure you have:")
    print("  1. Installed dependencies: pip install -r requirements.txt")
    print("  2. Generated sample corpus: python generate_sample_corpus.py")
    print()
    
    # Choose which examples to run
    # Uncomment the examples you want to run
    
    # example_serial_processing()
    # example_parallel_processing()
    # example_save_results()
    # example_custom_metrics()
    # example_compare_modes()
    
    print("\n" + "=" * 60)
    print("To run examples:")
    print("  1. Uncomment the example function calls above")
    print("  2. Run: python examples.py")
    print("=" * 60)


if __name__ == '__main__':
    main()
