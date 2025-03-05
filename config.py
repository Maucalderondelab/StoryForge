
import os
from dotenv import load_dotenv
from typing import TypeDict, List, Dict, Optional, Literal
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
class StoryState(TypeDict):
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
    needs_search: NotRequired[bool]
    search_results: NotRequired[Dict]
    iterations: NotRequired[int]

    # Outputs
    title: NotRequired[str]
    story: NotRequired[str]
    chapters: NotRequired[List[Dict[str, str]]]
