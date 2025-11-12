#!/usr/bin/env python3
"""
Generate sample documents for testing the pipeline.
Creates a small corpus with different document types.
"""

import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import argparse


def create_sample_text(output_dir: Path, filename: str, content: str, format_type: str = 'txt'):
    """Create a sample text file (txt, md, or html)."""
    filepath = output_dir / filename
    
    if format_type == 'html':
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Sample Document</title>
</head>
<body>
    <h1>Sample Document</h1>
    <p>{content}</p>
    <p>This is a test document for the ingestion pipeline.</p>
</body>
</html>"""
        with open(filepath, 'w') as f:
            f.write(html_content)
    elif format_type == 'md':
        md_content = f"""# Sample Document

{content}

This is a test document for the ingestion pipeline.

## Features
- Markdown support
- Easy to read
- Lightweight
"""
        with open(filepath, 'w') as f:
            f.write(md_content)
    else:  # txt
        with open(filepath, 'w') as f:
            f.write(f"Sample Document\n\n")
            f.write(f"{content}\n\n")
            f.write(f"This is a test document for the ingestion pipeline.\n")
    
    print(f"Created: {filepath}")


def create_sample_image(output_dir: Path, filename: str, text: str):
    """Create a sample image with text."""
    # Create a simple image with text
    img = Image.new('RGB', (800, 400), color='white')
    draw = ImageDraw.Draw(img)
    
    # Try to use a default font, fall back to default if not available
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 40)
    except:
        font = ImageFont.load_default()
    
    # Draw text
    draw.text((50, 150), text, fill='black', font=font)
    draw.text((50, 250), "Test image for OCR pipeline", fill='blue', font=font)
    
    filepath = output_dir / filename
    img.save(filepath)
    print(f"Created: {filepath}")


def main():
    """Generate sample documents."""
    parser = argparse.ArgumentParser(description='Generate sample documents for testing')
    parser.add_argument(
        '--output-dir',
        type=str,
        default='sample_corpus',
        help='Directory to save sample documents'
    )
    parser.add_argument(
        '--count',
        type=int,
        default=5,
        help='Number of documents of each type to create'
    )
    
    args = parser.parse_args()
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 60)
    print("Generating Sample Document Corpus")
    print("=" * 60)
    print(f"Output directory: {output_dir}")
    print(f"Documents per type: {args.count}")
    print()
    
    # Generate sample documents
    topics = [
        "Machine Learning in Healthcare",
        "Climate Change and Sustainability",
        "The Future of Artificial Intelligence",
        "Quantum Computing Basics",
        "Blockchain Technology Overview",
        "Space Exploration Milestones",
        "Renewable Energy Solutions",
        "Cybersecurity Best Practices",
        "Data Science Applications",
        "Cloud Computing Architecture"
    ]
    
    for i in range(min(args.count, len(topics))):
        topic = topics[i]
        
        # Create HTML files
        create_sample_text(
            output_dir,
            f'document_{i+1}.html',
            f'This document discusses {topic}. '
            f'It contains important information about the subject matter. '
            f'Document ID: {i+1}',
            'html'
        )
        
        # Create Markdown files
        create_sample_text(
            output_dir,
            f'document_{i+1}.md',
            f'This document discusses {topic}. '
            f'It contains important information about the subject matter. '
            f'Document ID: {i+1}',
            'md'
        )
        
        # Create text files
        create_sample_text(
            output_dir,
            f'document_{i+1}.txt',
            f'Topic: {topic}\n\nThis is a test document for the ingestion pipeline.\nDocument ID: {i+1}',
            'txt'
        )
        
        # Create Image
        create_sample_image(
            output_dir,
            f'image_{i+1}.png',
            f'{topic}'
        )
    
    print()
    print("=" * 60)
    print(f"Sample corpus created in: {output_dir}")
    print(f"Total files: {len(list(output_dir.iterdir()))}")
    print()
    print("To test the pipeline, run:")
    print(f"  python benchmark.py --corpus-path {output_dir} --mode both")
    print("=" * 60)


if __name__ == '__main__':
    main()
