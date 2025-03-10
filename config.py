
import os
from dotenv import load_dotenv
from typing import TypedDict, List, Dict, Optional, Literal
from typing_extensions import NotRequired

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL_NAME = "gpt-4o-mini"
MODEL_NAME_REASONING = "o1-mini"

PPLX_API_KEY = os.getenv("PPLX_API_KEY")
PPLX_MODEL_NAME = "llama-3.1-sonar-small-128k-online"

LANGSMITH_TRACING = True
LANGSMITH_ENDPOINT = "https://api.smith.langchain.com"
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
LANGSMITH_PROJECT = "StoryForge"


# Create the state class fr the app and agent integration
class StoryState(TypedDict):
    # UI inputs

    prompt: str
    story_type: Literal[
        "Moral & Reflecction",
        "Historical",
        "Terror"
    ]
    length: Literal[
        "Short",
        "Medium",
        "Long"
    ]
    style: str

    # Processing Variables
    iterations: Optional[int]
    sample_stories: Optional[Dict]
    
    # Research variables
    questions: Optional[List[str]]
    research_results: Optional[List[Dict]]
    research_history: Optional[Dict]
    
    # Story building variables
    chapters: Optional[List[Dict[str, str]]]
    
    # Evaluation variables
    evaluation: Optional[Dict]
    
    # Outputs
    title: Optional[str]
    story: Optional[str]
    final_title: Optional[str]
    final_story: Optional[str]
