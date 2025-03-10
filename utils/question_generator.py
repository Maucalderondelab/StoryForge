from typing import Dict, List, Any
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

# Import from config
import os
import sys

from config import MODEL_NAME_REASONING


def generate_research_questions_dynamic(state):
    """
    Here we dynamically generate research questions based on the story prompt uing a reasoning model, gpt-o1-mini
    
    Args:
        The state with the promp and type of stoty    
    
    Returns:
        Updated state with research questions
    """ 
    llm_reasoning = ChatOpenAI(model = MODEL_NAME_REASONING)

    # Extract the information of the prompt
    prompt= state.get("prompt", "")
    story_type = state.get("story_type", "Historical")

    print(prompt)
    print(story_type)

    # Create a prompt to generate research questions
    question_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a historical researcher helping to create an accurate historical story.
    Generate 4-6 specific research questions that will be essential for creating an accurate and
    engaging historical story based on the user's request.
    
    Focus on questions that will:
    1. Establish accurate historical context and setting
    2. Uncover important historical events, figures, or social conditions
    3. Reveal details about daily life, customs, or technology of the period
    4. Identify potential historical conflicts or tensions to drive the narrative
    
    Formulate clear, specific questions that can be answered through research.
    """),
            ("user", f"""Generate research questions for a historical story based on this prompt:
    STORY PROMPT: {prompt}
    
    Return only the questions, one per line, with no preamble or explanation.
    Each question should be direct and specific, appropriate for a search engine or historical database.
    """)
        ])
    # Generate questions
    response = llm.invoke(question_prompt)

    # Parse the response into a list of questions
    questions = [q.strip() for q in response.content.strip().split('\n') if q.strip()]

    return {
        **state,
        "questions": questions
    }
