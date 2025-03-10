from langgraph.graph import StateGraph, START, END
import os

from typing import Dict, Any, Literal, Optional, List

# Import all the agent components
from agents.story_builder import StoryBuilder
from agents.critic_agent import CriticAgent
from agents.style_adapter import StyleAdapter
from utils.research_tool import generate_research_questions, perplexity_search

# Create instances of our agents
story_builder = StoryBuilder()
critic = CriticAgent()
style_adapter = StyleAdapter()

def routes_by_story_type(state):
    """
    Routes the story request based on the story type selected in the UI.
    """
    story_type = state.get("story_type", "Moral & Reflection")
    print(f"Routing story of type: {story_type}")
    
    return story_type

def create_workflow(State):
    """
    Create a unified workflow for story generation based on UI input.
    All branches are integrated into a single StateGraph.
    
    Args:
        State: The state type definition
        
    Returns:
        Compiled workflow
    """
    # Initialize the state graph
    workflow = StateGraph(State)
    
    # Add the main router node
    workflow.add_node("router", routes_by_story_type)
    
    # ===== HISTORICAL BRANCH NODES =====
    # Add nodes for the research phase
    workflow.add_node("historical_research_questions", generate_research_questions)
    workflow.add_node("historical_research", perplexity_search)
    
    # Add nodes for story creation and refinement
    workflow.add_node("historical_story_building", story_builder.create_story_draft)
    workflow.add_node("historical_evaluation", critic.evaluate_story)
    workflow.add_node("historical_style", style_adapter.adapt_style)
    
    # ===== MORAL & REFLECTION BRANCH =====
    # For now, just a placeholder that returns the state
    def process_moral_reflection(state):
        # In a real implementation, this would have its own logic
        # For now, we're just setting some default values
        sample_story = state.get("sample_stories", {}).get("Moral & Reflection", {})
        state["title"] = sample_story.get("title", "A Moral Tale")
        state["story"] = sample_story.get("story", "Once upon a time...")
        state["chapters"] = sample_story.get("chapters", [])
        return state
        
    workflow.add_node("moral_reflection", process_moral_reflection)
    
    # ===== TERROR BRANCH =====
    # For now, just a placeholder that returns the state
    def process_terror(state):
        # In a real implementation, this would have its own logic
        # For now, we're just setting some default values
        sample_story = state.get("sample_stories", {}).get("Terror", {})
        state["title"] = sample_story.get("title", "A Terror Tale")
        state["story"] = sample_story.get("story", "It was a dark and stormy night...")
        state["chapters"] = sample_story.get("chapters", [])
        return state
        
    workflow.add_node("terror", process_terror)
    
    # ===== DEFINE THE EDGES =====
    # From router to each branch's first node
    workflow.add_conditional_edges(
        "router",
        lambda state: state.get("story_type", "Moral & Reflection"),
        {
            "Historical": "historical_research_questions",
            "Moral & Reflection": "moral_reflection",
            "Terror": "terror"
        }
    )
    
    # Historical branch flow
    workflow.add_edge("historical_research_questions", "historical_research")
    workflow.add_edge("historical_research", "historical_story_building")
    workflow.add_edge("historical_story_building", "historical_evaluation")
    
    # Conditional edge based on evaluation result
    workflow.add_conditional_edges(
        "historical_evaluation",
        lambda state: "historical_style" if state.get("evaluation", {}).get("approved", False) else "historical_story_building",
        {
            "historical_style": "historical_style",
            "historical_story_building": "historical_story_building"
        }
    )
    
    # Connect all endpoints to END
    workflow.add_edge("historical_style", END)
    workflow.add_edge("moral_reflection", END)
    workflow.add_edge("terror", END)
    
    # Set the entry point
    workflow.set_entry_point("router")
    
    return workflow.compile()
