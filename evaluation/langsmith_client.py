"""
LangSmith Client for Construction Agent Evaluation.

This module provides a class-based interface for interacting with LangSmith
to create datasets and examples for agent evaluation.
"""

import logging
from typing import List, Dict, Any, Optional
from langsmith import Client

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
                      description: str = "Dataset for Construction Agent evaluation") -> str:
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
            return dataset.id
            
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
            
            # Create examples
            self.client.create_examples(
                inputs=[{"Question": q} for q in questions],
                outputs=[{"Answer": a} for a in answers],
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


def main():
    """Main function to demonstrate usage of the LangSmithDatasetManager class."""
    try:
        print("=== LangSmith Dataset Manager Demo ===\n")
        
        # Initialize the manager
        manager = LangSmithDatasetManager()
        
        # Sample data (you can replace this with your actual data)
        sample_questions = [
            "How many square meters is Room A?",
            "What's the area of the corridor in this plan?",
            "Can you tell me the scale of Drawing 101?"
        ]
        
        sample_answers = [
            "clear_tool_call_measure_area",
            "clear_tool_call_measure_area",
            "clear_tool_call_get_scale"
        ]
        
        # Create dataset
        dataset_id = manager.create_dataset(
            dataset_name="intent_classification_dataset",
            description="Dataset to evaluate Construction Agent's intent classification"
        )
        
        print(f"Dataset created with ID: {dataset_id}")
        
        # Add examples to dataset
        success = manager.add_examples_to_dataset(
            dataset_id=dataset_id,
            questions=sample_questions,
            answers=sample_answers
        )
        
        if success:
            print(f"Successfully added {len(sample_questions)} examples to dataset")
        else:
            print("Failed to add examples to dataset")
        
        return dataset_id
        
    except Exception as e:
        logger.error(f"Error in main execution: {e}")
        raise


if __name__ == "__main__":
    main() 