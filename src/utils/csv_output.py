"""CSV output module for benchmark results."""

import pandas as pd
from pathlib import Path
from typing import Dict, Any
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class CSVOutput:
    """Handle CSV output for benchmark results."""
    
    def __init__(self, output_dir: str = 'results'):
        """
        Initialize CSV output handler.
        
        Args:
            output_dir: Directory to save CSV files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def save_results(self, stats: Dict[str, Any], mode: str, run_id: str = None) -> str:
        """
        Save benchmark statistics to CSV.
        
        Args:
            stats: Dictionary of statistics
            mode: Processing mode ('serial' or 'parallel')
            run_id: Optional run identifier
            
        Returns:
            Path to saved CSV file
        """
        if run_id is None:
            run_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Prepare data for CSV
        data = {
            'run_id': run_id,
            'mode': mode,
            'timestamp': datetime.now().isoformat()
        }
        
        # Flatten nested dictionaries
        for key, value in stats.items():
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    data[f'{key}_{sub_key}'] = sub_value
            else:
                data[key] = value
        
        # Create DataFrame
        df = pd.DataFrame([data])
        
        # Save to CSV
        filename = f'benchmark_{mode}_{run_id}.csv'
        filepath = self.output_dir / filename
        
        try:
            df.to_csv(filepath, index=False)
            logger.info(f"Results saved to {filepath}")
            return str(filepath)
        except Exception as e:
            logger.error(f"Error saving results to CSV: {e}")
            raise
    
    def append_results(self, stats: Dict[str, Any], mode: str, summary_file: str = 'benchmark_summary.csv'):
        """
        Append results to a summary CSV file.
        
        Args:
            stats: Dictionary of statistics
            mode: Processing mode
            summary_file: Name of summary CSV file
        """
        filepath = self.output_dir / summary_file
        
        # Prepare data
        data = {
            'mode': mode,
            'timestamp': datetime.now().isoformat()
        }
        
        for key, value in stats.items():
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    data[f'{key}_{sub_key}'] = sub_value
            else:
                data[key] = value
        
        df_new = pd.DataFrame([data])
        
        try:
            # Append to existing file or create new one
            if filepath.exists():
                df_existing = pd.read_csv(filepath)
                df_combined = pd.concat([df_existing, df_new], ignore_index=True)
                df_combined.to_csv(filepath, index=False)
            else:
                df_new.to_csv(filepath, index=False)
            
            logger.info(f"Results appended to {filepath}")
        except Exception as e:
            logger.error(f"Error appending results to CSV: {e}")
            raise
    
    def create_comparison_report(self, serial_file: str, parallel_file: str, output_file: str = 'comparison.csv'):
        """
        Create a comparison report from serial and parallel runs.
        
        Args:
            serial_file: Path to serial results CSV
            parallel_file: Path to parallel results CSV
            output_file: Name of output comparison file
        """
        try:
            df_serial = pd.read_csv(serial_file)
            df_parallel = pd.read_csv(parallel_file)
            
            # Merge on common columns
            comparison = pd.merge(
                df_serial, df_parallel,
                on=['run_id'], 
                suffixes=('_serial', '_parallel'),
                how='outer'
            )
            
            # Calculate speedup if both have throughput
            if 'throughput_docs_per_sec_serial' in comparison.columns and 'throughput_docs_per_sec_parallel' in comparison.columns:
                comparison['speedup'] = comparison['throughput_docs_per_sec_parallel'] / comparison['throughput_docs_per_sec_serial']
            
            filepath = self.output_dir / output_file
            comparison.to_csv(filepath, index=False)
            logger.info(f"Comparison report saved to {filepath}")
            
        except Exception as e:
            logger.error(f"Error creating comparison report: {e}")
            raise
