# %%
"""
Construction Agent Evaluation - Interactive Python Mode
This file can be run interactively in Cursor with cell markers (# %%)
"""

# %%
# Import required libraries
import os
import json
import asyncio
from typing import Dict, List, Any
from dotenv import load_dotenv
# LangSmith imports
from langsmith import Client
from langsmith.evaluation import EvaluationResult, EvaluationResults
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langsmith import aevaluate
from constructionagent.agent.core import AgentGraph
from constructionagent.agent.graph_loader import graph
from sklearn.metrics import precision_score, recall_score, f1_score, accuracy_score

# %%
# Configuration
load_dotenv()
PROJECT_NAME = "construction-agent-eval"
INTENT_DATASET_NAME = "agent_intent_evaluation"

    
# Initialize LangSmith client
client = Client()
print("✅ LangSmith client initialized")

# %%
# Custom Evaluator
class ConstructionAgentEvaluator():
    """Custom evaluator for the Construction Agent."""
    
    def __init__(self):
        # self.judge_llm = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key='AIzaSyDtVT5t83CPc5Gkzn22B86-S0rlev2jby8', temperature=0)
        self.judge_llm = ChatOpenAI(
            model="gpt-4o", 
            temperature=0,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        print('************self.judge_llm*********', self.judge_llm)
        self.graph = None
        self.pred_labels = []
        self.ref_labels = []
    
    async def build_graph(self):
        self.graph = await graph()

    async def intent_evaluation(self, outputs: dict, reference_outputs: dict) -> bool:
        instructions = (
            '''Given a Json which represents the agent's response to the user's query:
            The Agent can perform the following tools calls: measure_area(region), get_scale(drawing), query_pipe_info(location)
                {{
                    "unrelated": true | false (True if agent thinks user's query is unrelated to its capabilities)
                    "intents": [
                        {{
                        "tool": "tool_name", (tool name agent thinks user is asking for)
                        "is_ambiguous": true | false, (True if agent thinks tool parameters are ambiguous)
                        "ambiguous_reason": "reason for ambiguity"
                        "arguments": {{
                            "arg1": "value or null"
                        }},
                        "missing_arguments": ["arg1"]
                        }},
                        {{
                        "tool": "tool_name",
                        "is_ambiguous": true | false,
                        "ambiguous_reason": "reason for ambiguity"
                        "arguments": {{
                            "arg1": "value"
                        }},
                        "missing_arguments": []
                        }}
                    ]
                }}
            Your task if to respond with one of these labels by critially analyzing the agent's response:
            1) "clear_tool_call_measure_area"
            2) "clear_tool_call_get_scale" 
            3) "clear_tool_call_query_pipe_info"
            4) "ambiguous_tool_intent"
            5) "multiple_tool_intents_with_ambiguity"
            6) "multiple_tool_intents_all_clear"
            7) "unrelated_query"
            Do not include anything else in your response.'''
        )
        # Our graph outputs a State dictionary, which in this case means
        # we'll have a 'messages' key and the final message should
        # be our actual answer.
        actual_answer = outputs["messages"][-1].content
        expected_answer = reference_outputs["Answer"]
        user_msg = (
            f"ACTUAL ANSWER: {actual_answer}"
            f"\n\nEXPECTED ANSWER: {expected_answer}"
        )
        response = await self.judge_llm.ainvoke(
            [
                {"role": "system", "content": instructions},
                {"role": "user", "content": user_msg}
            ]
        )
        predicted_label = response.content.strip().lower()
        expected_label = expected_answer.strip().lower()

        self.pred_labels.append(predicted_label)
        self.ref_labels.append(expected_label)
        is_correct = predicted_label == expected_label
        return EvaluationResult(
            key="Intent_Evaluation",
            score=1.0 if is_correct else 0.0,
            comment=f"predicted={predicted_label}, expected={expected_label}"
        )
    

    def summary_classification_metrics(self, runs: List[Any], examples: List[Any]) -> EvaluationResults:
        """Computes summary metrics: precision, recall, F1, accuracy."""

        preds = self.pred_labels
        refs = self.ref_labels

        self.pred_labels = []
        self.ref_labels = []

        if not preds or not refs:
            print("Warning: pred_labels or ref_labels are empty. Cannot compute summary metrics.")
            return EvaluationResults(results=[])
        if len(preds) != len(refs):
            print(f"Warning: Mismatch in lengths of predictions ({len(preds)}) and references ({len(refs)}). Cannot compute accurate metrics.")
            return EvaluationResults(results=[])

        return EvaluationResults(results=[
            EvaluationResult(key="precision", score=precision_score(refs, preds, average="macro", zero_division=0)),
            EvaluationResult(key="recall", score=recall_score(refs, preds, average="macro", zero_division=0)),
            EvaluationResult(key="f1_score", score=f1_score(refs, preds, average="macro", zero_division=0)),
            EvaluationResult(key="accuracy", score=accuracy_score(refs, preds))
        ])
# %%
    async def run_individual_node(self, target_node, langsmith_dataset_name: str, evaluators: list, summary_evaluators: list) -> bool:
        
        node_target = self.graph.nodes[target_node]

        node_experiment_results = await aevaluate(
            node_target,
            data=langsmith_dataset_name,
            evaluators=evaluators,
            summary_evaluators=summary_evaluators,
            # --- ADD THIS LINE FOR THE FIX ---
            max_concurrency=1, # Start with 1 to ensure no parallel calls initially
            # ---------------------------------
        )

import openai
async def main():
    obj = ConstructionAgentEvaluator()
    await obj.build_graph()
    await obj.run_individual_node('Query_Validation', INTENT_DATASET_NAME, [obj.intent_evaluation], [obj.summary_classification_metrics])

asyncio.run(main())


