from typing import Dict, Any, List, Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

# Import from config
import os
import sys
from config import MODEL_NAME

class StyleAdapter:
    """
    Agent responsible for adapting the story to a consistent style and voice.
    """
    
    def __init__(self, model_name: str = None):
        """Initialize the style adapter."""
        self.model_name = model_name or MODEL_NAME
        self.llm = ChatOpenAI(model=self.model_name, temperature=0.6)
        
        # Initialize style templates
        self.style_templates = {
            "Classic storytelling": """
Use a timeless narrative voice with rich description and measured pacing.
Employ elegant, literary language that feels both accessible and sophisticated.
Balance dialogue, action, and description in the tradition of classic storytellers.
Use a third-person omniscient or limited perspective.
""",
            "Modern": """
Use a contemporary, direct voice with concise sentences and vivid imagery.
Incorporate modern sensibilities while maintaining historical accuracy.
Balance showing and telling with a focus on character perspectives.
Use a mix of short and medium-length sentences for rhythm.
""",
            "Poetic": """
Use lyrical, evocative language rich with metaphor and sensory detail.
Create a rhythm in your prose with careful attention to sentence structure and flow.
Focus on emotional resonance and the inner experiences of characters.
Use vivid imagery that appeals to all senses.
""",
            "Conversational": """
Write as if telling the story directly to a friend, with a warm and engaging tone.
Use a natural, accessible vocabulary with occasional colloquialisms (appropriate to the period).
Include rhetorical questions and direct address to create immediacy.
Balance informal tone with the gravity appropriate to historical events.
"""
        }
    
    def adapt_style(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply consistent style to the final story.
        
        Args:
            state: Current state with approved story
            
        Returns:
            Updated state with styled final story
        """
        # Extract necessary information from state
        title = state.get("title", "Untitled")
        story = state.get("story", "")
        style = state.get("style", "Classic storytelling")
        
        # Get the style template or default to classic
        style_guidance = self.style_templates.get(style, self.style_templates["Classic storytelling"])
        
        style_prompt = ChatPromptTemplate.from_messages([
            ("system", f"""You are a master of literary style adaptation. Your task is to refine and polish the 
given story to consistently align with the requested style, while preserving the story's substance, 
historical accuracy, and narrative structure.

STYLE GUIDANCE:
{style_guidance}
"""),
            ("user", f"""Adapt the following historical story to match the "{style}" style consistently throughout:

TITLE: {title}

STORY:
{story}

Maintain the same plot, characters, and historical details, but enhance the prose to consistently reflect 
the requested style. Focus on:
1. Voice and tone
2. Sentence structure and rhythm
3. Descriptive approach
4. Overall mood and atmosphere

Retain the title and overall structure, but polish every paragraph to create a cohesive stylistic experience.
Return the complete styled story.
""")
        ])
        
        response = self.llm.invoke(style_prompt)
        
        # The styled story is the complete response
        styled_story = response.content
        
        # Extract title if it appears in the styled version (assuming it's on the first line)
        lines = styled_story.split('\n')
        styled_title = lines[0].replace('#', '').strip()
        if styled_title.lower().startswith('title:'):
            styled_title = styled_title[6:].strip()
            # Remove the title line from the story text
            styled_story = '\n'.join(lines[1:]).strip()
        else:
            styled_title = title
        
        # Update the state
        state["final_title"] = styled_title
        state["final_story"] = styled_story
        
        return state
