from typing import Dict, Any, List, Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
import json

# Import from config
import os
import sys
from config import MODEL_NAME

class StoryBuilder:
    """
    Agent responsible for building story drafts based on research and user requirements.
    """
    
    def __init__(self, model_name: str = None):
        """Initialize the story builder."""
        self.model_name = model_name or MODEL_NAME
        self.llm = ChatOpenAI(model=self.model_name, temperature=0.7)
        
        # Initialize system prompts
        self.system_prompt = """You are a masterful storyteller who specializes in creating 
historically accurate and engaging stories. Your task is to craft a story that is:
1. Historically accurate and authentic
2. Engaging and well-structured
3. Appropriate for the requested length and style

Use the research provided to ensure historical accuracy while weaving an interesting narrative.
"""

    def _create_chapter_outline(self, research_results: List[Dict], 
                               prompt: str, 
                               story_length: str) -> List[Dict]:
        """
        Create an outline with chapters for the story.
        
        Args:
            research_results: List of research results
            prompt: User's story prompt
            story_length: Requested story length (Short, Medium, Long)
            
        Returns:
            List of chapter dictionaries with titles and descriptions
        """
        # Determine number of chapters based on length
        chapters_count = {
            "Short": 3,
            "Medium": 5,
            "Long": 7
        }.get(story_length, 5)
        
        # Format research for the prompt
        research_text = "\n\n".join([
            f"RESEARCH ON {item['topic'].upper()}:\n{item['result']}" 
            for item in research_results
        ])
        
        outline_prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("user", f"""Based on this user request and historical research, create a chapter outline for a story:

USER REQUEST: {prompt}
STORY LENGTH: {story_length} (approximately {chapters_count} chapters)

HISTORICAL RESEARCH:
{research_text}

Create a compelling chapter outline that follows good narrative structure (setup, conflict, resolution) 
while ensuring historical accuracy. For each chapter, provide:
1. A title
2. A brief description of what happens in that chapter

Format your response as a JSON array of chapter objects, each with "title" and "description" fields.
""")
        ])
        
        response = self.llm.invoke(outline_prompt)
        
        # Parse the response - expecting JSON format
        try:
            chapters = json.loads(response.content)
            # Add time markers for YouTube chapters
            for i, chapter in enumerate(chapters):
                # Simple time calculation - assume each chapter is ~2 minutes for Short, ~3 for Medium, ~4 for Long
                minutes_per_chapter = {"Short": 2, "Medium": 3, "Long": 4}.get(story_length, 3)
                minutes = i * minutes_per_chapter
                chapter["time"] = f"{minutes:02d}:00"
            return chapters
        except json.JSONDecodeError:
            # If the response isn't valid JSON, try to extract it from the text
            import re
            json_match = re.search(r'```json\n(.*?)\n```', response.content, re.DOTALL)
            if json_match:
                chapters = json.loads(json_match.group(1))
            else:
                # Create a simple fallback outline
                chapters = [
                    {"title": f"Chapter {i+1}", "description": "Story events", "time": f"{i*3:02d}:00"} 
                    for i in range(chapters_count)
                ]
            return chapters

    def create_story_draft(self, state):
        """
        Create a story draft based on research and user requirements.
        
        Args:
            state: Current state with research results and user requirements
            
        Returns:
            Updated state with story draft and chapters
        """
        # Extract necessary information from state
        user_prompt = state.get("prompt", "")
        story_type = state.get("story_type", "Historical")
        story_length = state.get("length", "Medium")
        style = state.get("style", "Classic storytelling")
        research_results = state.get("research_results", [])
        iteration = state.get("iterations", 0)
        
        # If we have evaluation feedback, include it
        feedback = state.get("evaluation", {}).get("feedback", "")
        
        # Get or create chapter outline
        if state.get("chapters") and iteration > 0:
            chapters = state.get("chapters")
        else:
            chapters = self._create_chapter_outline(
                research_results=research_results,
                prompt=user_prompt,
                story_length=story_length
            )
        
        # Format research for the prompt
        research_text = "\n\n".join([
            f"RESEARCH ON {item['topic'].upper()}:\n{item['result']}" 
            for item in research_results
        ])
        
        # Format chapters for the prompt
        chapters_text = "\n".join([
            f"Chapter {i+1}: {chapter['title']} - {chapter['description']}"
            for i, chapter in enumerate(chapters)
        ])
        
        # Determine target word count based on length
        word_counts = {
            "Short": "800-1200",
            "Medium": "1500-2500",
            "Long": "3000-5000"
        }.get(story_length, "1500-2500")
        
        # Create the draft prompt
        draft_prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("user", f"""Create a compelling {story_type.lower()} story based on the following:

                        USER REQUEST: {prompt}
                        STYLE: {style}
                        TARGET WORD COUNT: {word_counts} words
                        
                        STORY OUTLINE:
                        {chapters_text}
                        
                        HISTORICAL RESEARCH:
                        {research_text}
                        
                        {"PREVIOUS FEEDBACK TO ADDRESS: " + feedback if feedback else ""}
                        
                        Write a complete story that:
                        1. Is historically accurate and authentic, using details from the research
                        2. Follows the chapter structure provided
                        3. Is engaging and well-written in the requested style
                        4. Has well-developed characters and an interesting plot
                        
                        Provide a compelling title for the story at the beginning.
                        """)
           ])
        
        # Generate the story draft
        response = self.llm.invoke(draft_prompt)
        
        # Extract title and story from the response
        content = response.content
        
        # Try to extract the title (assuming it's on the first line)
        lines = content.split('\n')
        title = lines[0].replace('#', '').strip()
        if title.lower().startswith('title:'):
            title = title[6:].strip()
        
        # The rest is the story
        story = '\n'.join(lines[1:]).strip()
        
        # Update the state
        state["title"] = title
        state["story"] = story
        state["chapters"] = chapters
        state["iterations"] = iteration + 1
        
        return state

def create_story_draft(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a story draft based on research and user requirements.
        
        Args:
            state: Current state with research results and user requirements
            
        Returns:
            Updated state with story draft and chapters
        """
        # Extract necessary information from state
        user_prompt = state.get("prompt", "")
        story_type = state.get("story_type", "Historical")
        story_length = state.get("length", "Medium")
        style = state.get("style", "Classic storytelling")
        research_results = state.get("research_results", [])
        iteration = state.get("iterations", 0)
        
        # Store sample stories if provided by the app for fallback
        sample_stories = state.get("sample_stories", {})
        
        # If we have evaluation feedback, include it
        feedback = state.get("evaluation", {}).get("feedback", "")
