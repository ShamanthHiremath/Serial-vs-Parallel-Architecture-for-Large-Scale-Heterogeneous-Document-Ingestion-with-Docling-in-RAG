# Contributing to Document Ingestion Benchmark

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/Serial-vs-Parallel-Architecture-for-Large-Scale-Heterogeneous-Document-Ingestion-with-Docling-in-RAG.git
   cd Serial-vs-Parallel-Architecture-for-Large-Scale-Heterogeneous-Document-Ingestion-with-Docling-in-RAG
   ```

3. **Set up development environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

4. **Create a branch** for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Guidelines

### Code Style

- Follow PEP 8 style guidelines for Python code
- Use meaningful variable and function names
- Add docstrings to all classes and functions
- Keep functions focused and single-purpose
- Maximum line length: 100 characters

### Module Structure

The project follows a modular architecture:

```
src/
├── pipeline/          # Core pipeline components
│   ├── document_loader.py
│   ├── ocr_processor.py
│   ├── embedding_processor.py
│   ├── faiss_indexer.py
│   ├── serial_pipeline.py
│   └── parallel_pipeline.py
└── utils/            # Utility modules
    ├── metrics.py
    └── csv_output.py
```

### Adding New Features

1. **Document Formats**: To add support for new document formats, extend `DocumentLoader` class
2. **Embedding Models**: Add new models by configuring `EmbeddingProcessor`
3. **Metrics**: Add new metrics to `MetricsCollector` class
4. **Pipeline Modes**: Create new pipeline classes inheriting common patterns

### Testing

Before submitting a pull request:

1. **Test structure**:
   ```bash
   python test_structure.py
   ```

2. **Test with sample corpus**:
   ```bash
   python generate_sample_corpus.py --count 3
   python benchmark.py --corpus-path sample_corpus --mode both
   ```

3. **Verify no errors** in the output and results are generated

### Documentation

- Update README.md if adding major features
- Update QUICKSTART.md if changing basic usage
- Add examples to examples.py for new functionality
- Include docstrings with parameter descriptions and return types

## Submitting Changes

1. **Commit your changes**:
   ```bash
   git add .
   git commit -m "Add feature: brief description"
   ```

2. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

3. **Create a Pull Request** on GitHub with:
   - Clear description of changes
   - Why the changes are needed
   - Any related issues
   - Test results

## Pull Request Guidelines

- One feature per pull request
- Include tests for new functionality
- Update documentation as needed
- Ensure code follows project style
- All checks must pass

## Reporting Issues

When reporting issues, include:

1. **Description**: Clear description of the problem
2. **Steps to reproduce**: Minimal steps to reproduce the issue
3. **Expected behavior**: What you expected to happen
4. **Actual behavior**: What actually happened
5. **Environment**: Python version, OS, GPU/CPU
6. **Logs**: Relevant error messages or log output

## Feature Requests

We welcome feature requests! Please include:

1. **Use case**: Describe your use case
2. **Proposed solution**: How you envision it working
3. **Alternatives**: Other approaches you considered
4. **Impact**: Who would benefit from this feature

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Help maintain a positive environment

## Questions?

- Open an issue for bugs or feature requests
- Check existing issues before creating new ones
- Provide clear, reproducible examples

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
