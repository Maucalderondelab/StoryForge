from typing import Dict, Any, List, Tuple, Optional, Literal
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END

# Import from config and utils
import os
import sys
from config import MODEL_NAME, MODEL_NAME_REASONING
from utils.research_tool import generate_research_questions, perplexity_search
from utils.question_generator import generate_research_questions_dynamic

class HistoricalOrchestrator:
    """
    Orchestrator for the Historical story generation branch.
    Coordinates research, story building, evaluation, and style adaptation.
    """
    
    def __init__(self):
        """Initialize the orchestrator with necessary components."""
        self.llm = ChatOpenAI(model=MODEL_NAME, temperature=0.7)
        self.reasoning_llm = ChatOpenAI(model=MODEL_NAME_REASONING, temperature=0.2)
    
    def orchestrate_historical_story(self):
        """
        Main entry point for the historical story orchestration.
        
        Args:
            state: Initial state from the user interface
            
        Returns:
            Final state with the completed story
        """
        # Step 1: Generate research questions based on the prompt
        state = generate_research_questions(state)
        
        # Step 2: Conduct research using Perplexity
        state = perplexity_search(state)
        
        # The rest of the workflow will be handled by the LangGraph nodes
        return state
    
    def create_orchestrator_graph(self, StoryState) -> StateGraph:
        """
        Create a LangGraph for the historical orchestrator workflow.
        
        Args:
            StoryState: Type definition for the state
            
        Returns:
            Compiled StateGraph for the historical orchestrator
        """
        # Create the state graph
        workflow = StateGraph(StoryState)
        
        # Add nodes for the research phase
        workflow.add_node("generate_questions", generate_research_questions)
        workflow.add_node("conduct_research", perplexity_search)
        
        # Placeholder nodes for other components that will be implemented
        workflow.add_node("story_building", lambda state: state)
        workflow.add_node("evaluation", lambda state: state)
        workflow.add_node("style_adaptation", lambda state: state)
        
        # Add edges for the workflow
        workflow.add_edge("generate_questions", "conduct_research")
        workflow.add_edge("conduct_research", "story_building")
        workflow.add_edge("story_building", "evaluation")
        
        # Add conditional edge from evaluation
        workflow.add_conditional_edges(
            "evaluation",
            lambda state: "style_adaptation" if state.get("evaluation", {}).get("approved", False) else "story_building",
            {
                "style_adaptation": "style_adaptation",
                "story_building": "story_building"
            }
        )
        
        workflow.add_edge("style_adaptation", END)
        
        # Set entry point
        workflow.set_entry_point("generate_questions")
        
        return workflow.compile()
