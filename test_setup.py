#!/usr/bin/env python3
"""
Quick test script to verify the pipeline setup and components.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that all required modules can be imported."""
    print("Testing imports...")
    
    try:
        from src.pipeline.document_loader import DocumentLoader
        print("✓ DocumentLoader imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import DocumentLoader: {e}")
        return False
    
    try:
        from src.pipeline.ocr_processor import OCRProcessor
        print("✓ OCRProcessor imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import OCRProcessor: {e}")
        return False
    
    try:
        from src.pipeline.embedding_processor import EmbeddingProcessor
        print("✓ EmbeddingProcessor imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import EmbeddingProcessor: {e}")
        return False
    
    try:
        from src.pipeline.faiss_indexer import FAISSIndexer
        print("✓ FAISSIndexer imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import FAISSIndexer: {e}")
        return False
    
    try:
        from src.pipeline.serial_pipeline import SerialPipeline
        print("✓ SerialPipeline imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import SerialPipeline: {e}")
        return False
    
    try:
        from src.pipeline.parallel_pipeline import ParallelPipeline
        print("✓ ParallelPipeline imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import ParallelPipeline: {e}")
        return False
    
    try:
        from src.utils.metrics import MetricsCollector
        print("✓ MetricsCollector imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import MetricsCollector: {e}")
        return False
    
    try:
        from src.utils.csv_output import CSVOutput
        print("✓ CSVOutput imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import CSVOutput: {e}")
        return False
    
    return True


def test_dependencies():
    """Test that all external dependencies are available."""
    print("\nTesting dependencies...")
    
    dependencies = [
        ('docx', 'python-docx'),
        ('PyPDF2', 'PyPDF2'),
        ('pptx', 'python-pptx'),
        ('PIL', 'Pillow'),
        ('easyocr', 'easyocr'),
        ('sentence_transformers', 'sentence-transformers'),
        ('faiss', 'faiss-cpu or faiss-gpu'),
        ('torch', 'torch'),
        ('psutil', 'psutil'),
        ('pandas', 'pandas'),
        ('numpy', 'numpy'),
        ('tqdm', 'tqdm'),
    ]
    
    all_available = True
    for module_name, package_name in dependencies:
        try:
            __import__(module_name)
            print(f"✓ {package_name} is available")
        except ImportError:
            print(f"✗ {package_name} is NOT available")
            all_available = False
    
    return all_available


def test_gpu_availability():
    """Test GPU availability."""
    print("\nTesting GPU availability...")
    
    try:
        import torch
        if torch.cuda.is_available():
            print(f"✓ CUDA is available")
            print(f"  GPU count: {torch.cuda.device_count()}")
            print(f"  GPU name: {torch.cuda.get_device_name(0)}")
            return True
        else:
            print("⚠ CUDA is not available (will use CPU)")
            return False
    except Exception as e:
        print(f"✗ Error checking GPU: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("Pipeline Setup Verification")
    print("=" * 60)
    
    imports_ok = test_imports()
    deps_ok = test_dependencies()
    gpu_ok = test_gpu_availability()
    
    print("\n" + "=" * 60)
    print("Summary:")
    print("=" * 60)
    print(f"Imports: {'PASS' if imports_ok else 'FAIL'}")
    print(f"Dependencies: {'PASS' if deps_ok else 'FAIL'}")
    print(f"GPU: {'Available' if gpu_ok else 'Not Available (will use CPU)'}")
    
    if imports_ok and deps_ok:
        print("\n✓ Setup verification PASSED!")
        print("You can now run benchmarks with: python benchmark.py --corpus-path <path>")
        return 0
    else:
        print("\n✗ Setup verification FAILED!")
        print("Please install missing dependencies: pip install -r requirements.txt")
        return 1


if __name__ == '__main__':
    sys.exit(main())
