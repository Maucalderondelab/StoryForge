from typing import Dict, Any, TypedDict, Optional
from langgraph.graph import StateGraph, END

# Import our agents and tools
from agents.historical_orchestrator import HistoricalOrchestrator
from agents.story_builder import StoryBuilder
from agents.critic_agent import CriticAgent
from agents.style_adapter import StyleAdapter
from utils.research_tool import generate_research_questions, perplexity_search
from utils.question_generator import generate_research_questions_dynamic

def create_historical_branch(StoryState):
    """
    Create the historical branch workflow with all components.
    
    Args:
        StoryState: Type definition for the state
        
    Returns:
        Compiled StateGraph for the historical branch
    """
    # Create agent instances
    story_builder = StoryBuilder()
    critic = CriticAgent()
    style_adapter = StyleAdapter()
    
    # Create the state graph
    workflow = StateGraph(StoryState)
    
    # Add nodes for the research phase
    workflow.add_node("generate_questions", generate_research_questions)
    workflow.add_node("research", perplexity_search)
    
    # Add nodes for story creation and refinement
    workflow.add_node("story_building", story_builder.create_story_draft)
    workflow.add_node("evaluation", critic.evaluate_story)
    workflow.add_node("style_adaptation", style_adapter.adapt_style)
    
    # Add edges for the workflow
    workflow.add_edge("generate_questions", "research")
    workflow.add_edge("research", "story_building")
    workflow.add_edge("story_building", "evaluation")
    
    # Add conditional edge from evaluation - either continue to style or go back for revisions
    workflow.add_conditional_edges(
        "evaluation",
        lambda state: "style_adaptation" if state.get("evaluation", {}).get("approved", False) else "story_building",
        {
            "style_adaptation": "style_adaptation",
            "story_building": "story_building"
        }
    )
    
    # Final edge to end
    workflow.add_edge("style_adaptation", END)
    
    # Set entry point
    workflow.set_entry_point("generate_questions")
    
    return workflow.compile()

def process_historical_story(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process a historical story request - wrapper function to call from main workflow
    
    Args:
        state: Initial state from the story router
        
    Returns:
        Final state with the completed story
    """
    # Create and run the historical branch workflow
    try:
        # Get the state type from the config or define it here
        from config import StoryState
        
        # Build and run the workflow
        workflow = create_historical_branch(StoryState)
        final_state = workflow.invoke(state)
        
        # Transfer the final story and title to the main state keys
        state["title"] = final_state.get("final_title", final_state.get("title", "Historical Tale"))
        state["story"] = final_state.get("final_story", final_state.get("story", ""))
        state["chapters"] = final_state.get("chapters", [])
        
        return state
    except Exception as e:
        # Log the error
        print(f"Error in historical branch: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Return a basic story as fallback
        state["title"] = "Historical Tale"
        state["story"] = f"Once upon a time in history... (Error: {str(e)})"
        state["chapters"] = []
        
        return state
