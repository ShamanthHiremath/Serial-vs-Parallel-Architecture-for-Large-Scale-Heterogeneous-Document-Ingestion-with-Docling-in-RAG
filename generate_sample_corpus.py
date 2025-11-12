#!/usr/bin/env python3
"""
Generate sample documents for testing the pipeline.
Creates a small corpus with different document types.
"""

import os
from pathlib import Path
from docx import Document
from pptx import Presentation
from pptx.util import Inches, Pt
from PIL import Image, ImageDraw, ImageFont
import argparse


def create_sample_docx(output_dir: Path, filename: str, content: str):
    """Create a sample DOCX file."""
    doc = Document()
    doc.add_heading('Sample Document', 0)
    doc.add_paragraph(content)
    doc.add_paragraph('This is a test document for the ingestion pipeline.')
    
    filepath = output_dir / filename
    doc.save(filepath)
    print(f"Created: {filepath}")


def create_sample_pptx(output_dir: Path, filename: str, content: str):
    """Create a sample PPTX file."""
    prs = Presentation()
    
    # Slide 1
    slide = prs.slides.add_slide(prs.slide_layouts[0])
    title = slide.shapes.title
    subtitle = slide.placeholders[1]
    title.text = "Sample Presentation"
    subtitle.text = content
    
    # Slide 2
    slide = prs.slides.add_slide(prs.slide_layouts[1])
    title = slide.shapes.title
    body = slide.placeholders[1]
    title.text = "Content Slide"
    body.text = "This is a test presentation for the ingestion pipeline."
    
    filepath = output_dir / filename
    prs.save(filepath)
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


def create_sample_pdf_text(output_dir: Path, filename: str, content: str):
    """Create a simple text file (will be converted to PDF manually or used as-is)."""
    # Note: Creating a real PDF requires additional libraries
    # For testing, we'll create a text file with .txt extension
    # Users can manually convert to PDF or we can add reportlab dependency
    filepath = output_dir / filename.replace('.pdf', '.txt')
    
    with open(filepath, 'w') as f:
        f.write(f"Sample PDF Document\n\n")
        f.write(f"{content}\n\n")
        f.write(f"This is a test document for the ingestion pipeline.\n")
    
    print(f"Created text file: {filepath}")
    print(f"Note: Install reportlab and run with --create-pdf to generate actual PDFs")


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
        
        # Create DOCX
        create_sample_docx(
            output_dir,
            f'document_{i+1}.docx',
            f'This document discusses {topic}. '
            f'It contains important information about the subject matter. '
            f'Document ID: {i+1}'
        )
        
        # Create PPTX
        create_sample_pptx(
            output_dir,
            f'presentation_{i+1}.pptx',
            f'Topic: {topic}'
        )
        
        # Create Image
        create_sample_image(
            output_dir,
            f'image_{i+1}.png',
            f'{topic}'
        )
        
        # Create text file (placeholder for PDF)
        create_sample_pdf_text(
            output_dir,
            f'document_{i+1}.pdf',
            f'This document discusses {topic}.'
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
