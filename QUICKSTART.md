# Quick Start Guide

This guide will help you get started with the Document Ingestion Benchmark pipeline in 5 minutes.

## Prerequisites

- Python 3.8 or higher
- pip package manager
- (Optional) CUDA-compatible GPU for acceleration

## Step 1: Install Dependencies

```bash
# Create and activate virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install required packages
pip install -r requirements.txt
```

**Note**: Installation may take 5-10 minutes as it downloads models and libraries.

## Step 2: Verify Installation

```bash
# Run the setup test
python test_setup.py
```

You should see "Setup verification PASSED!" if everything is installed correctly.

## Step 3: Generate Sample Documents

```bash
# Create a sample corpus for testing
python generate_sample_corpus.py --count 5
```

This creates a `sample_corpus/` directory with sample DOCX, PPTX, and image files.

## Step 4: Run Your First Benchmark

```bash
# Run both serial and parallel modes on the sample corpus
python benchmark.py --corpus-path sample_corpus --mode both
```

This will:
- Process all documents in serial mode
- Process all documents in parallel mode
- Display performance metrics for both
- Save results to CSV files in the `results/` directory

## Step 5: View Results

Results are saved in the `results/` directory:
- `benchmark_serial_<timestamp>.csv` - Serial mode results
- `benchmark_parallel_<timestamp>.csv` - Parallel mode results
- `benchmark_summary.csv` - Cumulative results from all runs

You can open these files in Excel, Google Sheets, or analyze them with pandas.

## Example Output

```
================================================================================
Document Ingestion Benchmark
================================================================================
Corpus path: sample_corpus
Mode: both
Device: cpu
Embedding model: all-MiniLM-L6-v2
Output directory: results
================================================================================

================================================================================
Running SERIAL pipeline
================================================================================
Processing documents: 100%|██████████| 15/15 [00:45<00:00,  3.03s/it]

Serial Results:
  Documents processed: 15
  Total time: 46.23 seconds
  Throughput: 0.32 docs/sec
  Latency (P50): 3.01 sec
  Latency (P95): 4.12 sec
  Latency (P99): 4.45 sec

================================================================================
Running PARALLEL pipeline
================================================================================
Processing documents: 100%|██████████| 15/15 [00:18<00:00,  1.23s/it]

Parallel Results:
  Documents processed: 15
  Total time: 18.45 seconds
  Throughput: 0.81 docs/sec
  Latency (P50): 1.18 sec
  Latency (P95): 1.56 sec
  Latency (P99): 1.78 sec
  Workers: 7

================================================================================
COMPARISON
================================================================================
  Speedup: 2.51x
  Serial throughput: 0.32 docs/sec
  Parallel throughput: 0.81 docs/sec
  Throughput improvement: 153.1%
```

## Common Options

### Run with GPU acceleration:
```bash
python benchmark.py --corpus-path sample_corpus --device cuda
```

### Run only serial mode:
```bash
python benchmark.py --corpus-path sample_corpus --mode serial
```

### Run only parallel mode with specific worker count:
```bash
python benchmark.py --corpus-path sample_corpus --mode parallel --num-workers 4
```

### Use a different embedding model:
```bash
python benchmark.py --corpus-path sample_corpus --embedding-model paraphrase-MiniLM-L6-v2
```

## Next Steps

1. **Test with your own documents**: Replace `sample_corpus` with your document directory
2. **Experiment with settings**: Try different worker counts, embedding models, and devices
3. **Analyze results**: Use the CSV files to create visualizations and analyze performance
4. **Scale up**: Test with larger corpora to see how performance scales

## Troubleshooting

**Problem**: Out of memory errors
- **Solution**: Reduce `--num-workers` or process fewer documents at once

**Problem**: GPU not detected
- **Solution**: Ensure CUDA is installed and run `nvidia-smi` to verify GPU availability

**Problem**: Slow processing
- **Solution**: Use `--device cuda` for GPU acceleration if available

**Problem**: Import errors
- **Solution**: Ensure all dependencies are installed: `pip install -r requirements.txt`

## Getting Help

- Check the [README.md](README.md) for detailed documentation
- Review the example commands above
- Check log files in `benchmark.log` for detailed error messages
