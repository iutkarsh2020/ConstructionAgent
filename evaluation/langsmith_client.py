"""
LangSmith Client for Construction Agent Evaluation.

This module provides a class-based interface for interacting with LangSmith
to create datasets and examples for agent evaluation.
"""

import logging
from typing import List, Dict, Any, Optional
from langsmith import Client
from dotenv import load_dotenv
from dataset_generator import DatasetGenerator
from langchain_core.messages import HumanMessage
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LangSmithDatasetManager:
    """
    A class to manage LangSmith datasets for Construction Agent evaluation.
    
    This class provides methods to:
    - Create datasets in LangSmith
    - Add examples to datasets
    """
    
    def __init__(self):
        """Initialize the LangSmith client."""
        self.client = Client()
        logger.info("LangSmith client initialized")
    
    def create_dataset(self, 
                      dataset_name: str, 
                      description: str = "Dataset for Construction Agent evaluation"):
        """
        Create a new dataset in LangSmith.
        
        Args:
            dataset_name: Name of the dataset to create
            description: Description of the dataset
            
        Returns:
            Dataset ID of the created dataset
            
        Raises:
            Exception: If dataset creation fails
        """
        try:
            logger.info(f"Creating dataset: {dataset_name}")
            
            dataset = self.client.create_dataset(
                dataset_name=dataset_name,
                description=description
            )
            
            logger.info(f"Dataset created successfully with ID: {dataset.id}")
            return dataset
            
        except Exception as e:
            logger.error(f"Error creating dataset '{dataset_name}': {e}")
            raise Exception(f"Failed to create dataset: {e}")
    
    def add_examples_to_dataset(self, 
                               dataset_id: str, 
                               questions: List[str], 
                               answers: List[str]) -> bool:
        """
        Add examples to an existing dataset.
        
        Args:
            dataset_id: ID of the dataset to add examples to
            questions: List of questions/inputs
            answers: List of corresponding answers/outputs
            
        Returns:
            True if successful, False otherwise
            
        Raises:
            ValueError: If input validation fails
            Exception: If adding examples fails
        """
        try:
            # Validate inputs
            if len(questions) != len(answers):
                raise ValueError(
                    f"Mismatch between questions ({len(questions)}) and answers ({len(answers)})"
                )
            
            if not questions:
                raise ValueError("Questions list cannot be empty")
            
            logger.info(f"Adding {len(questions)} examples to dataset: {dataset_id}")
            
            # Create examples with the correct format
            # Each example should be a single dictionary with 'messages' key containing HumanMessage objects
            examples = []
            for question, answer in zip(questions, answers):
                example = {
                    "messages": [HumanMessage(content=question)],
                    "Answer": answer
                }
                examples.append(example)
            
            # Create examples in LangSmith with the correct format
            # Each input should be: {'messages': [HumanMessage(content=question)]}
            # Each output should be: {'Answer': answer}
            inputs = [{"messages": [HumanMessage(content=q)]} for q in questions]
            outputs = [{"Answer": a} for a in answers]
            
            self.client.create_examples(
                inputs=inputs,
                outputs=outputs,
                dataset_id=dataset_id
            )
            
            logger.info(f"Successfully added {len(questions)} examples to dataset")
            return True
            
        except ValueError as e:
            logger.error(f"Input validation error: {e}")
            raise
        except Exception as e:
            logger.error(f"Error adding examples to dataset '{dataset_id}': {e}")
            raise Exception(f"Failed to add examples to dataset: {e}")



load_dotenv() 
ls = LangSmithDatasetManager()
s = DatasetGenerator("config/evaluation_data.yaml")
ls_dataset = ls.create_dataset(s.dataset_config.name, s.dataset_config.description)
ls.add_examples_to_dataset(ls_dataset.id, s.dataset_config.inputs, s.dataset_config.expected_outputs)



