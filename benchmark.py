#!/usr/bin/env python3
"""
Main benchmark script for comparing serial vs parallel document ingestion.

This script provides a CLI to run document ingestion benchmarks using either
serial or parallel processing modes.
"""

import argparse
import logging
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.pipeline.serial_pipeline import SerialPipeline
from src.pipeline.parallel_pipeline import ParallelPipeline
from src.utils.csv_output import CSVOutput


def setup_logging(verbose: bool = False):
    """Set up logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('benchmark.log')
        ]
    )


def main():
    """Main entry point for the benchmark script."""
    parser = argparse.ArgumentParser(
        description='Benchmark serial vs parallel document ingestion pipeline',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Required arguments
    parser.add_argument(
        '--corpus-path',
        type=str,
        required=True,
        help='Path to document corpus (directory or single file)'
    )
    
    parser.add_argument(
        '--mode',
        type=str,
        choices=['serial', 'parallel', 'both'],
        default='both',
        help='Processing mode: serial, parallel, or both'
    )
    
    # Optional arguments
    parser.add_argument(
        '--device',
        type=str,
        choices=['cpu', 'cuda'],
        default='cpu',
        help='Device to use for processing (cpu or cuda)'
    )
    
    parser.add_argument(
        '--embedding-model',
        type=str,
        default='all-MiniLM-L6-v2',
        help='Sentence-transformer model name'
    )
    
    parser.add_argument(
        '--num-workers',
        type=int,
        default=None,
        help='Number of parallel workers (default: CPU count - 1)'
    )
    
    parser.add_argument(
        '--use-threads',
        action='store_true',
        help='Use threads instead of processes for parallel mode'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        default='results',
        help='Directory to save benchmark results'
    )
    
    parser.add_argument(
        '--run-id',
        type=str,
        default=None,
        help='Run identifier for result files'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)
    
    # Validate corpus path
    corpus_path = Path(args.corpus_path)
    if not corpus_path.exists():
        logger.error(f"Corpus path does not exist: {args.corpus_path}")
        sys.exit(1)
    
    # Initialize CSV output
    csv_output = CSVOutput(output_dir=args.output_dir)
    
    logger.info("=" * 80)
    logger.info("Document Ingestion Benchmark")
    logger.info("=" * 80)
    logger.info(f"Corpus path: {args.corpus_path}")
    logger.info(f"Mode: {args.mode}")
    logger.info(f"Device: {args.device}")
    logger.info(f"Embedding model: {args.embedding_model}")
    logger.info(f"Output directory: {args.output_dir}")
    logger.info("=" * 80)
    
    results = {}
    
    # Run serial pipeline
    if args.mode in ['serial', 'both']:
        logger.info("\n" + "=" * 80)
        logger.info("Running SERIAL pipeline")
        logger.info("=" * 80)
        
        try:
            serial_pipeline = SerialPipeline(
                device=args.device,
                embedding_model=args.embedding_model
            )
            
            serial_stats = serial_pipeline.process_corpus(args.corpus_path)
            results['serial'] = serial_stats
            
            # Save results
            csv_file = csv_output.save_results(serial_stats, 'serial', args.run_id)
            csv_output.append_results(serial_stats, 'serial')
            
            logger.info(f"\nSerial Results:")
            logger.info(f"  Documents processed: {serial_stats.get('num_documents', 0)}")
            logger.info(f"  Total time: {serial_stats.get('total_time_seconds', 0):.2f} seconds")
            logger.info(f"  Throughput: {serial_stats.get('throughput_docs_per_sec', 0):.2f} docs/sec")
            logger.info(f"  Latency (P50): {serial_stats.get('latency_p50_sec', 0):.4f} sec")
            logger.info(f"  Latency (P95): {serial_stats.get('latency_p95_sec', 0):.4f} sec")
            logger.info(f"  Latency (P99): {serial_stats.get('latency_p99_sec', 0):.4f} sec")
            logger.info(f"  Results saved to: {csv_file}")
            
        except Exception as e:
            logger.error(f"Serial pipeline failed: {e}", exc_info=True)
    
    # Run parallel pipeline
    if args.mode in ['parallel', 'both']:
        logger.info("\n" + "=" * 80)
        logger.info("Running PARALLEL pipeline")
        logger.info("=" * 80)
        
        try:
            parallel_pipeline = ParallelPipeline(
                device=args.device,
                embedding_model=args.embedding_model,
                num_workers=args.num_workers,
                use_threads=args.use_threads
            )
            
            parallel_stats = parallel_pipeline.process_corpus(args.corpus_path)
            results['parallel'] = parallel_stats
            
            # Save results
            csv_file = csv_output.save_results(parallel_stats, 'parallel', args.run_id)
            csv_output.append_results(parallel_stats, 'parallel')
            
            logger.info(f"\nParallel Results:")
            logger.info(f"  Documents processed: {parallel_stats.get('num_documents', 0)}")
            logger.info(f"  Total time: {parallel_stats.get('total_time_seconds', 0):.2f} seconds")
            logger.info(f"  Throughput: {parallel_stats.get('throughput_docs_per_sec', 0):.2f} docs/sec")
            logger.info(f"  Latency (P50): {parallel_stats.get('latency_p50_sec', 0):.4f} sec")
            logger.info(f"  Latency (P95): {parallel_stats.get('latency_p95_sec', 0):.4f} sec")
            logger.info(f"  Latency (P99): {parallel_stats.get('latency_p99_sec', 0):.4f} sec")
            logger.info(f"  Workers: {parallel_stats.get('num_workers', 0)}")
            logger.info(f"  Results saved to: {csv_file}")
            
        except Exception as e:
            logger.error(f"Parallel pipeline failed: {e}", exc_info=True)
    
    # Compare results if both modes were run
    if args.mode == 'both' and 'serial' in results and 'parallel' in results:
        logger.info("\n" + "=" * 80)
        logger.info("COMPARISON")
        logger.info("=" * 80)
        
        serial_time = results['serial'].get('total_time_seconds', 1)
        parallel_time = results['parallel'].get('total_time_seconds', 1)
        speedup = serial_time / parallel_time if parallel_time > 0 else 0
        
        serial_throughput = results['serial'].get('throughput_docs_per_sec', 0)
        parallel_throughput = results['parallel'].get('throughput_docs_per_sec', 0)
        
        logger.info(f"  Speedup: {speedup:.2f}x")
        logger.info(f"  Serial throughput: {serial_throughput:.2f} docs/sec")
        logger.info(f"  Parallel throughput: {parallel_throughput:.2f} docs/sec")
        logger.info(f"  Throughput improvement: {(parallel_throughput/serial_throughput - 1)*100:.1f}%")
    
    logger.info("\n" + "=" * 80)
    logger.info("Benchmark completed successfully")
    logger.info("=" * 80)


if __name__ == '__main__':
    main()
