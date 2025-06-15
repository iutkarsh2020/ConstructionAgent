"""
Dataset Generator for Construction Agent Evaluation.

This module provides a class-based approach to generate evaluation datasets
from configuration files, following production best practices.
"""

import pandas as pd
import yaml
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class DatasetConfig:
    """Configuration data class for dataset settings."""
    name: str
    description: str
    version: str
    created_date: str
    inputs: List[str]
    expected_outputs: List[str]
    output_settings: Dict[str, Any]

class DatasetGenerator:
    """
    A class to generate evaluation datasets from configuration files.
    
    This class follows production best practices including:
    - Proper error handling and validation
    - Type hints and documentation
    - Logging for debugging and monitoring
    - Separation of concerns
    - Configurable output formats
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the DatasetGenerator.
        
        Args:
            config_path: Path to the YAML configuration file.
                        If None, uses default path.
        
        Raises:
            FileNotFoundError: If config file doesn't exist
            yaml.YAMLError: If config file is malformed
        """
        self.config_path = config_path or "evaluation/config/evaluation_data.yaml"
        self.config = self._load_config()
        self.dataset_config = self._parse_config()
        
        logger.info(f"DatasetGenerator initialized with config: {self.config_path}")
    
    def _load_config(self) -> Dict[str, Any]:
        """
        Load configuration from YAML file.
        
        Returns:
            Dictionary containing configuration data
            
        Raises:
            FileNotFoundError: If config file doesn't exist
            yaml.YAMLError: If config file is malformed
        """
        try:
            config_file = Path(self.config_path)
            if not config_file.exists():
                raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
            
            with open(config_file, 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file)
            
            logger.info(f"Configuration loaded successfully from {self.config_path}")
            return config
            
        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML configuration: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error loading configuration: {e}")
            raise
    
    def _parse_config(self) -> DatasetConfig:
        """
        Parse configuration into a structured data class.
        
        Returns:
            DatasetConfig object containing parsed configuration
            
        Raises:
            KeyError: If required configuration keys are missing
            ValueError: If configuration data is invalid
        """
        try:
            # Validate data consistency
            inputs = self.config['inputs']
            expected_outputs = self.config['expected_outputs']
            
            if len(inputs) != len(expected_outputs):
                raise ValueError(
                    f"Mismatch between inputs ({len(inputs)}) and expected_outputs ({len(expected_outputs)})"
                )
            
            return DatasetConfig(
                name=self.config['dataset']['name'],
                description=self.config['dataset']['description'],
                version=self.config['dataset']['version'],
                created_date=self.config['dataset']['created_date'],
                inputs=inputs,
                expected_outputs=expected_outputs,
                output_settings=self.config['output']
            )
            
        except KeyError as e:
            logger.error(f"Configuration parsing error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error parsing configuration: {e}")
            raise
    
    def generate_dataframe(self) -> pd.DataFrame:
        """
        Generate a pandas DataFrame from the configuration data.
        
        Returns:
            DataFrame containing question-answer pairs
            
        Raises:
            ValueError: If data generation fails
        """
        try:
            qa_pairs = []
            for i, (question, expected_output) in enumerate(
                zip(self.dataset_config.inputs, self.dataset_config.expected_outputs)
            ):
                qa_pairs.append({
                    "Question": question,
                    "Expected_output": expected_output
                })
            
            df = pd.DataFrame(qa_pairs)
            logger.info(f"Generated DataFrame with {len(df)} rows")
            return df
            
        except Exception as e:
            logger.error(f"Error generating DataFrame: {e}")
            raise ValueError(f"Failed to generate DataFrame: {e}")
    
    
    def save_to_csv(self, df: pd.DataFrame, output_path: Optional[str] = None) -> str:
        """
        Save DataFrame to CSV file.
        
        Args:
            df: DataFrame to save
            output_path: Custom output path. If None, uses config default
            
        Returns:
            Path to the saved CSV file
            
        Raises:
            OSError: If file cannot be written
        """
        try:
            if output_path is None:
                output_dir = Path(self.dataset_config.output_settings['output_directory'])
                output_dir.mkdir(parents=True, exist_ok=True)
                
                filename = self.dataset_config.output_settings['csv_filename']
                if self.dataset_config.output_settings.get('include_timestamp', False):
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    name, ext = filename.rsplit('.', 1)
                    filename = f"{name}_{timestamp}.{ext}"
                
                output_path = output_dir / filename
            
            df.to_csv(output_path, index=False)
            logger.info(f"DataFrame saved to CSV: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Error saving CSV file: {e}")
            raise OSError(f"Failed to save CSV file: {e}")
    
d = DatasetGenerator('config/tool_invocation_evaluation.yaml')
df = d.generate_dataframe()
d.save_to_csv(df, 'tool_invocation_evaluation.csv')
print(df)