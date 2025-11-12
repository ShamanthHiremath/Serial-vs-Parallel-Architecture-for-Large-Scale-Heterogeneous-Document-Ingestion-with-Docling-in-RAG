# Serial vs Parallel Document Ingestion Benchmark

A modular Python pipeline to benchmark **serial vs parallel document ingestion** using Docling for RAG (Retrieval-Augmented Generation) pipelines. This tool helps you analyze performance differences between sequential and parallel processing of heterogeneous document corpora.

## Features

- **Multi-format Support**: PDF, DOCX, PPTX, and image files (JPG, PNG, BMP, TIFF)
- **GPU-Accelerated OCR**: Uses EasyOCR with CUDA support for image and scanned document processing
- **Sentence Embeddings**: Leverages sentence-transformers for high-quality document embeddings
- **FAISS Indexing**: Efficient vector storage and similarity search
- **Comprehensive Metrics**: 
  - Throughput (documents/second)
  - Latency percentiles (P50, P95, P99)
  - CPU and GPU usage monitoring
  - Memory consumption tracking
- **CSV Output**: Results exported to CSV for easy analysis
- **Flexible CLI**: Command-line interface with flags for mode, device, and corpus path

## Architecture

The pipeline consists of modular components:

1. **DocumentLoader**: Extracts text from various document formats
2. **OCRProcessor**: Applies EasyOCR to images and scanned documents
3. **EmbeddingProcessor**: Generates embeddings using sentence-transformers
4. **FAISSIndexer**: Builds and manages vector index
5. **MetricsCollector**: Tracks performance and resource metrics
6. **SerialPipeline**: Processes documents sequentially
7. **ParallelPipeline**: Processes documents using multiprocessing/multithreading

## Installation

### Prerequisites

- Python 3.8 or higher
- CUDA-compatible GPU (optional, for GPU acceleration)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/ShamanthHiremath/Serial-vs-Parallel-Architecture-for-Large-Scale-Heterogeneous-Document-Ingestion-with-Docling-in-RAG.git
cd Serial-vs-Parallel-Architecture-for-Large-Scale-Heterogeneous-Document-Ingestion-with-Docling-in-RAG
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. (Optional) For GPU support, install PyTorch with CUDA:
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

## Usage

### Basic Usage

Run the benchmark on a corpus of documents:

```bash
python benchmark.py --corpus-path /path/to/documents --mode both
```

### CLI Options

```
Required Arguments:
  --corpus-path PATH    Path to document corpus (directory or single file)

Optional Arguments:
  --mode {serial,parallel,both}
                        Processing mode (default: both)
  --device {cpu,cuda}   Device for processing (default: cpu)
  --embedding-model MODEL
                        Sentence-transformer model (default: all-MiniLM-L6-v2)
  --num-workers N       Number of parallel workers (default: CPU count - 1)
  --use-threads         Use threads instead of processes for parallel mode
  --output-dir DIR      Directory to save results (default: results)
  --run-id ID           Custom run identifier
  --verbose             Enable verbose logging
```

### Examples

**1. Compare serial vs parallel on CPU:**
```bash
python benchmark.py --corpus-path ./docs --mode both --device cpu
```

**2. Run parallel mode with GPU acceleration:**
```bash
python benchmark.py --corpus-path ./docs --mode parallel --device cuda --num-workers 4
```

**3. Test with a specific embedding model:**
```bash
python benchmark.py --corpus-path ./docs --embedding-model paraphrase-MiniLM-L6-v2
```

**4. Run serial mode only with custom output directory:**
```bash
python benchmark.py --corpus-path ./docs --mode serial --output-dir ./my_results
```

## Output

### Console Output

The benchmark provides detailed progress and results:
- Document processing progress bar
- Per-mode statistics (documents processed, throughput, latency)
- Resource usage metrics
- Comparison between serial and parallel (when both modes run)

### CSV Files

Results are saved in the specified output directory:

- `benchmark_serial_<timestamp>.csv`: Serial mode results
- `benchmark_parallel_<timestamp>.csv`: Parallel mode results  
- `benchmark_summary.csv`: Cumulative results from all runs

### Metrics Collected

- **Performance**:
  - Total processing time
  - Throughput (docs/sec)
  - Per-document latency (mean, median, P50, P95, P99, min, max)
  
- **Resources**:
  - CPU usage (mean, max, min)
  - Memory usage in MB (mean, max, min)
  - GPU usage and memory (if available)
  
- **Document Statistics**:
  - Number of documents processed
  - Document type distribution
  - Total data size processed

## Project Structure

```
.
├── benchmark.py              # Main CLI script
├── requirements.txt          # Python dependencies
├── src/
│   ├── pipeline/
│   │   ├── document_loader.py      # Document loading
│   │   ├── ocr_processor.py        # OCR processing
│   │   ├── embedding_processor.py  # Embedding generation
│   │   ├── faiss_indexer.py        # FAISS indexing
│   │   ├── serial_pipeline.py      # Serial processing
│   │   └── parallel_pipeline.py    # Parallel processing
│   └── utils/
│       ├── metrics.py              # Metrics collection
│       └── csv_output.py           # CSV output handling
├── results/                  # Benchmark results (created automatically)
└── README.md
```

## Performance Tips

1. **GPU Acceleration**: Use `--device cuda` for significant speedup on OCR and embeddings
2. **Worker Count**: For parallel mode, experiment with `--num-workers` (typically CPU count - 1)
3. **Model Selection**: Smaller embedding models process faster but may have lower quality
4. **Thread vs Process**: Use `--use-threads` for I/O-bound workloads, omit for CPU-bound

## Supported File Formats

- **PDF**: Extracted text or OCR for scanned PDFs
- **DOCX**: Microsoft Word documents
- **PPTX**: PowerPoint presentations
- **Images**: JPG, JPEG, PNG, BMP, TIFF (processed with OCR)

## Troubleshooting

**Issue**: Out of memory errors
- Solution: Reduce `--num-workers` or process smaller batches

**Issue**: GPU not detected
- Solution: Ensure CUDA is installed and PyTorch is built with CUDA support

**Issue**: Slow OCR processing
- Solution: Enable GPU with `--device cuda` or reduce image resolution

**Issue**: Import errors
- Solution: Ensure all dependencies are installed: `pip install -r requirements.txt`

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Citation

If you use this tool in your research, please cite:

```bibtex
@software{serial_parallel_docling,
  title={Serial vs Parallel Document Ingestion Benchmark},
  author={Shamanth Hiremath},
  year={2024},
  url={https://github.com/ShamanthHiremath/Serial-vs-Parallel-Architecture-for-Large-Scale-Heterogeneous-Document-Ingestion-with-Docling-in-RAG}
}
```
