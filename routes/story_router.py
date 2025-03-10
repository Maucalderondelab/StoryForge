from typing import Dict, Literal, Any, List, Optional

def routes_by_story_type(state) -> Literal["Moral & Reflection", "Historical", "Terror"]:
    """
    Routes the story request based on the story type selected in the UI.

    Args:
        state: The state of the story type selected in the UI.

    Returns:
        The name of the next node route as a string literal
    """
    # Get story_type from state, with a default value of "Moral & Reflection"
    story_type = state.get("story_type", "Moral & Reflection")

    print(f"Routing story of type: {story_type}")

    # IMPORTANT: This function should ONLY return the name of the next node,
    # not modify the state or return the state dictionary

    # Route based on the story type from the UI
    if story_type == "Historical":
        return "Historical"
    elif story_type == "Terror":
        return "Terror"
    elif story_type == "Moral & Reflection" or not story_type:
        return "Moral & Reflection"
    else:
        # Default to Moral & Reflection for any unknown type
        print(f"Unknown story type: {story_type}, defaulting to 'Moral & Reflection'")
        return "Moral & Reflection"
