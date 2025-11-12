# Architecture Overview

This document describes the architecture and design decisions of the Document Ingestion Benchmark pipeline.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      CLI Interface                           │
│                    (benchmark.py)                            │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ├─────────────┬────────────────────┐
                   ▼             ▼                    ▼
        ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
        │   Serial     │  │  Parallel    │  │   Metrics    │
        │   Pipeline   │  │  Pipeline    │  │  Collector   │
        └──────┬───────┘  └──────┬───────┘  └──────┬───────┘
               │                 │                  │
               └────────┬────────┘                  │
                        │                           │
        ┌───────────────┴────────────────┐         │
        │       Pipeline Components       │         │
        ├────────────────────────────────┤         │
        │  • DocumentLoader              │         │
        │  • OCRProcessor                │         │
        │  • EmbeddingProcessor          │         │
        │  • FAISSIndexer                │         │
        └───────────────┬────────────────┘         │
                        │                           │
                        └───────────┬───────────────┘
                                    ▼
                        ┌──────────────────────┐
                        │    CSV Output        │
                        └──────────────────────┘
```

## Core Components

### 1. Document Loader (`document_loader.py`)

**Purpose**: Load and extract text from various document formats

**Supported Formats**:
- PDF: PyPDF2 for text extraction
- DOCX: python-docx for Word documents
- PPTX: python-pptx for PowerPoint presentations
- Images: PIL for image validation (requires OCR)

**Design Pattern**: Strategy pattern for different file type handlers

**Key Methods**:
- `load_document()`: Main entry point for loading a document
- `find_documents()`: Recursively find documents in a directory
- `_load_pdf()`, `_load_docx()`, etc.: Format-specific loaders

### 2. OCR Processor (`ocr_processor.py`)

**Purpose**: Extract text from images and scanned documents using EasyOCR

**Features**:
- GPU acceleration support (CUDA)
- Multi-language support (default: English)
- Batch processing capability

**Design Considerations**:
- Lazy initialization of EasyOCR reader (expensive operation)
- Configurable device (CPU/GPU)
- Error handling for corrupted images

### 3. Embedding Processor (`embedding_processor.py`)

**Purpose**: Generate semantic embeddings using sentence-transformers

**Features**:
- Configurable embedding models
- GPU acceleration support
- Text length truncation for memory management

**Default Model**: all-MiniLM-L6-v2
- Dimension: 384
- Speed: Fast
- Quality: Good balance

**Alternative Models**:
- `paraphrase-MiniLM-L6-v2`: Paraphrase similarity
- `all-mpnet-base-v2`: Higher quality, slower
- `multi-qa-MiniLM-L6-cos-v1`: Question answering

### 4. FAISS Indexer (`faiss_indexer.py`)

**Purpose**: Build and manage vector index for similarity search

**Index Types**:
- **Flat** (default): Exact search, best for small datasets (<10K)
- **IVF**: Approximate search, scalable to millions
- **HNSW**: Fast approximate search, graph-based

**Design**:
- L2 distance with normalized vectors (cosine similarity)
- Automatic training for IVF indices
- Metadata storage alongside vectors

### 5. Serial Pipeline (`serial_pipeline.py`)

**Purpose**: Process documents sequentially

**Flow**:
1. Find documents in corpus
2. For each document:
   - Load document
   - Apply OCR if needed
   - Generate embeddings
   - Record metrics
3. Build FAISS index
4. Calculate statistics

**Advantages**:
- Predictable resource usage
- Simple debugging
- Lower memory overhead

**Best For**:
- Small corpora (<100 documents)
- Limited RAM
- Single-threaded environments

### 6. Parallel Pipeline (`parallel_pipeline.py`)

**Purpose**: Process documents in parallel using multiprocessing/threading

**Flow**:
1. Find documents in corpus
2. Create worker pool
3. Distribute documents to workers
4. Each worker:
   - Initializes own components
   - Processes assigned documents
   - Returns results
5. Collect results and build index
6. Calculate statistics

**Concurrency Options**:
- **Processes** (default): True parallelism, higher overhead
- **Threads**: Lower overhead, limited by GIL for CPU-bound work

**Worker Count**:
- Default: CPU count - 1
- GPU: Typically 1-2 workers per GPU
- Configurable via `--num-workers`

**Advantages**:
- Significant speedup on multi-core systems
- Better hardware utilization
- Faster processing of large corpora

**Trade-offs**:
- Higher memory usage (each worker loads models)
- Inter-process communication overhead
- More complex error handling

### 7. Metrics Collector (`utils/metrics.py`)

**Purpose**: Collect and calculate performance metrics

**Metrics Categories**:

**Performance**:
- Throughput (documents/second)
- Latency (mean, median, P50, P95, P99, min, max)
- Total processing time

**Resources**:
- CPU usage (mean, max, min)
- Memory consumption (MB)
- GPU usage and memory (if available)

**Data**:
- Document count
- Document type distribution
- Total data processed (MB)

**Implementation**:
- Continuous monitoring during processing
- Statistical calculations using numpy
- Optional GPU monitoring via GPUtil

### 8. CSV Output (`utils/csv_output.py`)

**Purpose**: Export results to CSV for analysis

**Features**:
- Per-run CSV files
- Cumulative summary file
- Comparison report generation
- Flattened nested dictionaries

**Files Generated**:
- `benchmark_serial_<timestamp>.csv`
- `benchmark_parallel_<timestamp>.csv`
- `benchmark_summary.csv`

## Processing Flow

### Serial Mode

```
Document 1 → Load → OCR → Embed → ┐
Document 2 → Load → OCR → Embed → ├→ FAISS Index → Results
Document 3 → Load → OCR → Embed → ┘
```

### Parallel Mode

```
         ┌→ Worker 1 → Load → OCR → Embed →┐
Docs → ──├→ Worker 2 → Load → OCR → Embed →├→ Collect → FAISS Index → Results
         └→ Worker N → Load → OCR → Embed →┘
```

## Design Decisions

### 1. Modular Architecture

**Why**: Separation of concerns, testability, extensibility

Each component has a single responsibility:
- DocumentLoader: File I/O
- OCRProcessor: Text extraction
- EmbeddingProcessor: Vector generation
- FAISSIndexer: Vector storage

### 2. Process-based Parallelism

**Why**: True parallelism for CPU-bound operations

- Python GIL limits threading effectiveness for CPU work
- Each process gets independent Python interpreter
- Better utilization of multi-core CPUs

**Trade-off**: Higher memory usage vs. performance gain

### 3. Lazy Component Initialization

**Why**: Reduce startup time and memory in parallel mode

- OCR reader initialized only when needed
- Embedding model loaded per worker
- Index built after all processing

### 4. Metrics Collection

**Why**: Comprehensive performance analysis

- Real-time system monitoring
- Statistical analysis (percentiles, not just averages)
- Resource usage tracking

### 5. CSV Output Format

**Why**: Universal compatibility and analysis

- Easy to open in Excel, Google Sheets, R, Python
- Timestamped files for historical comparison
- Summary file for trend analysis

## Performance Characteristics

### Serial Pipeline

**Time Complexity**: O(n) where n = number of documents
**Space Complexity**: O(1) - single document in memory
**Best Case**: Small corpora, limited resources
**Worst Case**: Large corpora with fast hardware

### Parallel Pipeline

**Time Complexity**: O(n/w) where w = number of workers
**Space Complexity**: O(w) - w documents in memory
**Best Case**: Large corpora, multi-core CPU
**Worst Case**: Small corpora (overhead > benefit)

**Speedup**: Typically 2-8x depending on:
- Number of CPU cores
- Document processing complexity
- I/O vs CPU bottleneck
- Memory bandwidth

## Scalability

### Vertical Scaling (Single Machine)

- **CPU**: Add more cores → More workers
- **RAM**: More memory → Larger batches
- **GPU**: Faster OCR and embeddings
- **SSD**: Faster document loading

### Horizontal Scaling (Future)

Potential extensions:
- Distributed processing (Dask, Ray)
- Cloud deployment (AWS Lambda, Azure Functions)
- Kubernetes orchestration
- Database backend for results

## Security Considerations

1. **Input Validation**: Check file types and sizes
2. **Resource Limits**: Prevent memory exhaustion
3. **Path Traversal**: Validate corpus paths
4. **Dependencies**: Use latest patched versions
5. **Code Execution**: Avoid unsafe deserialization

## Extensibility Points

1. **New Document Formats**: Add handlers to DocumentLoader
2. **Custom OCR**: Replace OCRProcessor implementation
3. **Different Embeddings**: Configure EmbeddingProcessor
4. **Alternative Indices**: Extend FAISSIndexer
5. **Custom Metrics**: Add to MetricsCollector
6. **Output Formats**: Extend CSVOutput (JSON, Parquet, etc.)

## Future Enhancements

1. **Streaming Processing**: Handle documents larger than RAM
2. **Incremental Indexing**: Update FAISS index without rebuild
3. **Distributed Mode**: Process across multiple machines
4. **Web Interface**: GUI for configuration and visualization
5. **Model Caching**: Share models between workers
6. **Async I/O**: Overlap I/O and computation
7. **Progress Persistence**: Resume interrupted runs
8. **A/B Testing**: Compare different configurations
