from typing import Dict, Any, List, Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
import json

# Import from config
import os
import sys
from config import MODEL_NAME_REASONING

class CriticAgent:
    """
    Agent responsible for evaluating story drafts and providing feedback for improvements.
    """
    
    def __init__(self, model_name: str = None):
        """Initialize the critic agent."""
        self.model_name = model_name or MODEL_NAME_REASONING
        self.llm = ChatOpenAI(model=self.model_name, temperature=0.2)
        
        # Initialize system prompts
        self.system_prompt = """You are a critical editor and historical authenticity expert.
Your job is to evaluate stories for:
1. Historical accuracy and authenticity
2. Narrative quality and engagement
3. Appropriate style and tone
4. Overall effectiveness

Provide constructive criticism and specific suggestions for improvement.
Be thorough but fair in your assessment.
"""

    def evaluate_story(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate a story draft and provide feedback.
        
        Args:
            state: Current state with story draft and research
            
        Returns:
            Updated state with evaluation results
        """
        # Extract necessary information from state
        title = state.get("title", "Untitled")
        story = state.get("story", "")
        user_prompt = state.get("prompt", "")
        story_type = state.get("story_type", "Historical")
        style = state.get("style", "Classic storytelling")
        research_results = state.get("research_results", [])
        iterations = state.get("iterations", 0)
        
        # Format research for the prompt
        research_text = "\n\n".join([
            f"RESEARCH ON {item['topic'].upper()}:\n{item['result']}" 
            for item in research_results
        ])
        
        evaluation_prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("user", f"""Evaluate this historical story draft based on the following criteria:

TITLE: {title}

STORY DRAFT:
{story}

USER REQUEST: {user_prompt}
STYLE REQUESTED: {style}
ITERATION: {iterations}

HISTORICAL RESEARCH USED:
{research_text}

Evaluate the story on:
1. Historical accuracy (Does it align with the research? Are there anachronisms?)
2. Narrative quality (Is it engaging? Does it have a clear structure?)
3. Style and tone (Does it match the requested style?)
4. Character development and dialogue (Are they authentic to the period?)
5. Overall impact (How effective is it as a story?)

Provide your evaluation in JSON format with these fields:
- scores: Object with numerical scores (1-10) for each criterion
- strengths: Array of the story's strongest points
- weaknesses: Array of areas needing improvement
- feedback: Specific, actionable feedback for improvement
- approved: Boolean indicating if the story is ready (true) or needs revisions (false)
""")
        ])
        
        response = self.llm.invoke(evaluation_prompt)
        
        # Parse the response - expecting JSON format
        try:
            evaluation = json.loads(response.content)
        except json.JSONDecodeError:
            # If the response isn't valid JSON, try to extract it from the text
            import re
            json_match = re.search(r'```json\n(.*?)\n```', response.content, re.DOTALL)
            if json_match:
                evaluation = json.loads(json_match.group(1))
            else:
                # Create a simple fallback evaluation
                evaluation = {
                    "scores": {
                        "historical_accuracy": 7,
                        "narrative_quality": 7,
                        "style_and_tone": 7,
                        "character_and_dialogue": 7,
                        "overall_impact": 7
                    },
                    "strengths": ["Good effort overall"],
                    "weaknesses": ["Needs some refinement"],
                    "feedback": "Consider revising for better historical accuracy and narrative flow.",
                    "approved": iterations >= 2  # Auto-approve after 2 iterations to prevent endless loops
                }
        
        # Update the state
        state["evaluation"] = evaluation
        
        return state
