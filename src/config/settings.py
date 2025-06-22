from typing import Dict, List, Any, Optional, TypedDict


class MainState(TypedDict):
    messages: List[Dict[str, Any]]  # User messages
    current_fable: str              # Input fable text
    tool_to_call: str               # Which tool subgraph to use
    processing_request: Dict        # Request info for the tool
    tool_output: Dict               # Output from selected tool
    final_story: str                # Final output after post-processing
    image_prompts: List[Dict]       # List of image prompts for visualization ← This line!

# Cell 3: Define Aesop State (for subgraph)
class AesopState(TypedDict):
    original_fable: str             # Original input text
    analysis: Dict                  # Analysis of the fable (moral, characters, etc)
    brainstorm: Dict                # Ideas for the story creation/modification
    generated_story: str            # The final story created by this tool
    human_approved: bool            # Human approval status  
    feedback: str                   # Human feedback text
    revision_request: str           # Specific revision instructions
    revision_count: int             # Track number of revisions
    image_prompts: List[Dict]       # Image prompts (moved from MainState)