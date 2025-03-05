from langgraph.graph import StateGraph, START, END
import os

from typing import Dict, Any, Literal, Optional, List

# Change the relative import to absolute
from routes.story_router import routes_by_story_type

def create_workflow(State):
    """
    Create the workflow for the story generation based on the UI input

    Args:
        state: The state of the UI

    Returns:
        Compiled workflow
    """

    # initialize the state
    router_builder = StateGraph(State)

    # Add the router Based on the UI
    router_builder.add_node("story_router", routes_by_story_type)
    
    # Add the notes
    router_builder.add_node("Moral & Reflection", lambda state: state)
    router_builder.add_node("Historical", lambda state: state)
    router_builder.add_node("Terror", lambda state: state)
    

    # Add the routing edge - this will use the route_by_story_type function
    # to determine which node to go to next
    router_builder.add_conditional_edges(
        "story_router",
        routes_by_story_type,
        {
            "Moral & Reflection": "Moral & Reflection",
            "Historical": "Historical", 
            "Terror": "Terror"
        }
    )
    # Add the end state
    router_builder.add_edge("Moral & Reflection", END)

    # Add creative path flow
    router_builder.add_edge("Historical", END)
    
    # Add ambigous path flow
    router_builder.add_edge("Terror", END)

    # Set the entry point
    router_builder.set_entry_point("story_router")
    
    
    return router_builder.compile()

