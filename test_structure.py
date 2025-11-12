#!/usr/bin/env python3
"""
Simple integration test that verifies the pipeline structure without requiring all dependencies.
This test checks the module structure and basic functionality.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))


def test_module_structure():
    """Test that all modules exist and have the expected structure."""
    print("Testing module structure...")
    
    # Test pipeline modules exist
    pipeline_dir = Path(__file__).parent / 'src' / 'pipeline'
    expected_modules = [
        'document_loader.py',
        'ocr_processor.py',
        'embedding_processor.py',
        'faiss_indexer.py',
        'serial_pipeline.py',
        'parallel_pipeline.py'
    ]
    
    for module in expected_modules:
        module_path = pipeline_dir / module
        if module_path.exists():
            print(f"  ✓ {module} exists")
        else:
            print(f"  ✗ {module} NOT found")
            return False
    
    # Test utils modules exist
    utils_dir = Path(__file__).parent / 'src' / 'utils'
    expected_utils = [
        'metrics.py',
        'csv_output.py'
    ]
    
    for util in expected_utils:
        util_path = utils_dir / util
        if util_path.exists():
            print(f"  ✓ {util} exists")
        else:
            print(f"  ✗ {util} NOT found")
            return False
    
    return True


def test_cli_script():
    """Test that the CLI script exists and is executable."""
    print("\nTesting CLI script...")
    
    benchmark_script = Path(__file__).parent / 'benchmark.py'
    if not benchmark_script.exists():
        print("  ✗ benchmark.py NOT found")
        return False
    
    print("  ✓ benchmark.py exists")
    
    # Check if it has a shebang
    with open(benchmark_script, 'r') as f:
        first_line = f.readline()
        if first_line.startswith('#!'):
            print("  ✓ benchmark.py has shebang")
        else:
            print("  ⚠ benchmark.py missing shebang (optional)")
    
    return True


def test_documentation():
    """Test that documentation exists."""
    print("\nTesting documentation...")
    
    readme = Path(__file__).parent / 'README.md'
    if not readme.exists():
        print("  ✗ README.md NOT found")
        return False
    
    print("  ✓ README.md exists")
    
    # Check README has key sections
    with open(readme, 'r') as f:
        content = f.read()
        
    required_sections = ['Installation', 'Usage', 'Features']
    for section in required_sections:
        if section in content:
            print(f"  ✓ README contains '{section}' section")
        else:
            print(f"  ⚠ README missing '{section}' section")
    
    return True


def test_requirements():
    """Test that requirements.txt exists and has expected dependencies."""
    print("\nTesting requirements...")
    
    req_file = Path(__file__).parent / 'requirements.txt'
    if not req_file.exists():
        print("  ✗ requirements.txt NOT found")
        return False
    
    print("  ✓ requirements.txt exists")
    
    with open(req_file, 'r') as f:
        content = f.read()
    
    required_packages = [
        'docling',
        'easyocr',
        'sentence-transformers',
        'faiss',
        'pandas'
    ]
    
    for package in required_packages:
        if package in content.lower():
            print(f"  ✓ requirements.txt includes {package}")
        else:
            print(f"  ✗ requirements.txt missing {package}")
            return False
    
    return True


def test_class_definitions():
    """Test that classes are properly defined (without importing dependencies)."""
    print("\nTesting class definitions...")
    
    # Read source files and check for class definitions
    tests = [
        ('src/pipeline/document_loader.py', 'DocumentLoader'),
        ('src/pipeline/ocr_processor.py', 'OCRProcessor'),
        ('src/pipeline/embedding_processor.py', 'EmbeddingProcessor'),
        ('src/pipeline/faiss_indexer.py', 'FAISSIndexer'),
        ('src/pipeline/serial_pipeline.py', 'SerialPipeline'),
        ('src/pipeline/parallel_pipeline.py', 'ParallelPipeline'),
        ('src/utils/metrics.py', 'MetricsCollector'),
        ('src/utils/csv_output.py', 'CSVOutput'),
    ]
    
    base_path = Path(__file__).parent
    
    for file_path, class_name in tests:
        full_path = base_path / file_path
        with open(full_path, 'r') as f:
            content = f.read()
        
        if f'class {class_name}' in content:
            print(f"  ✓ {class_name} defined in {file_path}")
        else:
            print(f"  ✗ {class_name} NOT found in {file_path}")
            return False
    
    return True


def test_gitignore():
    """Test that .gitignore exists and has important patterns."""
    print("\nTesting .gitignore...")
    
    gitignore = Path(__file__).parent / '.gitignore'
    if not gitignore.exists():
        print("  ✗ .gitignore NOT found")
        return False
    
    print("  ✓ .gitignore exists")
    
    with open(gitignore, 'r') as f:
        content = f.read()
    
    important_patterns = ['__pycache__', '*.pyc', 'venv/', '*.csv', '*.log']
    for pattern in important_patterns:
        if pattern in content:
            print(f"  ✓ .gitignore includes {pattern}")
        else:
            print(f"  ⚠ .gitignore missing {pattern}")
    
    return True


def main():
    """Run all structure tests."""
    print("=" * 70)
    print("Pipeline Structure Verification (No Dependencies Required)")
    print("=" * 70)
    print()
    
    tests = [
        ("Module Structure", test_module_structure),
        ("CLI Script", test_cli_script),
        ("Documentation", test_documentation),
        ("Requirements", test_requirements),
        ("Class Definitions", test_class_definitions),
        (".gitignore", test_gitignore),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"  ✗ Error running test: {e}")
            results[test_name] = False
    
    print("\n" + "=" * 70)
    print("Summary:")
    print("=" * 70)
    
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{test_name:.<40} {status}")
    
    all_passed = all(results.values())
    
    print()
    if all_passed:
        print("✓ All structure tests PASSED!")
        print("\nNext steps:")
        print("  1. Install dependencies: pip install -r requirements.txt")
        print("  2. Run setup verification: python test_setup.py")
        print("  3. Generate sample corpus: python generate_sample_corpus.py")
        print("  4. Run benchmark: python benchmark.py --corpus-path sample_corpus --mode both")
        return 0
    else:
        print("✗ Some structure tests FAILED!")
        print("Please review the output above for details.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
