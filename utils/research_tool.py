from typing import Dict, List, Any, Optional, TypedDict
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_community.chat_models import ChatPerplexity

# Import from config and modules
import os
import sys

from config import PPLX_API_KEY, PPLX_MODEL_NAME
from utils.question_generator import generate_research_questions_dynamic

class ResearchResult(TypedDict):
    question: str
    answer: str
    citations: List[Any]

def perplexity_search(state):
    """
    Seach in perplexity to obtain more information

    Args:
        State: Current state containing the questions for the research

    Return:
        Update state with research results
    """


    current_iteration = state.get('iteration', 0)
    print(f"\n🔍 PERPLEXITY SEARCH PHASE - Iteration {current_iteration}")

    chat_perplexity = ChatPerplexity(
        api_key = PPLX_API_KEY,
        model = PPLX_MODEL_NAME,
        temperature = 0.1
    )

    questions = state.get("questions", [])
    research_history = state.get("research_history", {})
    current_search = []

    for question in questions:
        message = [
            SystemMessage(content="You are a helpful research assistant. Provide detailed, factual answers with historical accuracy."),
            HumanMessage(content=question)
        ]

        try:
            response = chat_perplexity.invoke(message)
            print(f"\n🔍 Question: {question}")
            print(f"💬 Answer: {response.content[:100]}...")

            # Create research result entry
            research_result = {
                "question": question,
                "answer": response.content,
                "citations": response.additional_kwargs.get('citations', []) if hasattr(response, 'additional_kwargs') else []
            }

            # Add to current search
            current_search.append(research_result)
        except Exception as e:
            print(f"🚨 Error researching the question: {question}: {str(e)}")

            # add error entry
            research_result = {
                "question": question,
                "answer": str(e),
                "citations": []
            }

            # Add to current search
            current_search.append(research_result)

       # Update research history with current findings
        updated_research_history = {
            **research_history,
            current_iteration: current_research
        }
        
        return {
            **state,  # Preserve existing state
            "research_results": current_research,  # Current iteration results
            "research_history": updated_research_history  # Historical record
        }


def generate_research_questions(state: Dict[str, Any]) -> Dict[str, Any]:
    """  Generate research questions based on the story prompt
 
     Args:
     state: Current state with story prompt
     
    Returns:
     Updated state with research questions
    """
    # Use the dynamic question generator
    return generate_research_questions_dynamic(state)
