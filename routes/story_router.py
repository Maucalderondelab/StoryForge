from typing import Dict, Literal, Any, List, Optional


def routes_by_story_type(state) -> Literal["Moral& & Reflection","Historical","Terror"]:
    """
    Routes the story request based on the story type selected in the UI.

    Args
        state: The state of the story type selected in the UI.

    Returns:
        The name of the next node route
    """

    story_type = state.get("story_tupe", "")

    print(f"Routing story of type: {story_type}")

# Route based on the story type from the UI
    if story_type == "Historical":
        return "Historical"
    elif story_type == "Terror":
        return "Terror"
    elif story_type == "Moral & Reflection":
        return "Moral & Reflection"
    
