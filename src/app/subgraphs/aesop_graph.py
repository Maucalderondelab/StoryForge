from typing import Dict, List, Any, Optional, TypedDict, Literal
import json
from datetime import datetime
import time
# config import
from config.settings import AesopState
from config.models_settings import openai_41_mini_client, gemini_imagen3_client
from config.logger import logger

# langhfraph imports
from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt, Command
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.runnables.graph import CurveStyle, MermaidDrawMethod, NodeStyles

# prompts import
from app.prompts.prompts import ANALYZE_FABLE_PROMPT, BRAINSTORM_STORY_PROMPT, GENERATE_STORY_AESOP_PROMPT, IMAGE_PROMPT_GENERATOR_PROMPT

# import metadata tracker
from metadata_tracker.metadata_tracker import track_node, track_llm_call, track_image_generation, metadata



# Node 1: Analyze Fable with tracking
@track_node("analyze_fable", "aesop_tool")
def analyze_fable(state: AesopState) -> Dict[str, Any]:
    """
    Analyzes the fable structure, characters, and moral
    """
    logger.info("== Aesop Subgraph: Analyze Fable ==")
    original_fable = state.get("original_fable", "")
    logger.info(f"Analyzing fable (length: {len(original_fable)} characters)")
    
    # Use LLM to analyze the fable with prompt from prompts.py
    system_prompt = ANALYZE_FABLE_PROMPT
    
    user_prompt = f"Analyze this fable:\n\n{original_fable}"
    
    response = openai_41_mini_client.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ])
    
    # Track the LLM call
    track_llm_call(
        node_name="analyze_fable",
        tool_name="aesop_tool",
        model="gpt-4.1-mini",
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        response_text=response.content
    )
    
    try:
        analysis = json.loads(response.content)
    except:
        # Fallback if JSON parsing fails
        logger.error("JSON parsing failed, using content as analysis")
        analysis = {
            "moral": response.content,
            "characters": [],
            "structure": {},
            "symbols": []
        }
    
    logger.info(f"Analysis complete: identified moral '{analysis.get('moral', '')[:50]}...'")
    return {"analysis": analysis}

@track_node("brainstorm_story", "aesop_tool")
# Node 2: Brainstorm Story
def brainstorm_story(state: AesopState) -> Dict[str, Any]:
    """
    Brainstorms ideas for story creation based on analysis
    """
    logger.info("== Aesop Subgraph: Brainstorm Story ==")
    original_fable = state.get("original_fable", "")
    analysis = state.get("analysis", {})
    
    logger.info(f"Brainstorming based on analysis of moral: {analysis.get('moral', '')[:50]}...")
    
    system_prompt = BRAINSTORM_STORY_PROMPT
    user_prompt = f"Original fable: {original_fable}\n\nAnalysis: {json.dumps(analysis, indent=2)}"
    response = openai_41_mini_client.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ])
    # Track the LLM call
    track_llm_call(
        node_name="brainstorm_story",
        tool_name="aesop_tool",
        model="gpt-4.1-mini",
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        response_text=response.content
    )
    try:
        brainstorm = json.loads(response.content)
    except:
        logger.error("JSON parsing failed, using content as brainstorm")
        brainstorm = {
            "moral_approaches": response.content,
            "variations": [],
            "character_ideas": [],
            "imagery": []
        }
    
    logger.info(f"Brainstorming complete: generated {len(brainstorm.keys())} idea categories")
    return {"brainstorm": brainstorm}


@track_node("generate_story_aessop", "aesop_tool")
# Node 3: Generate Story
def generate_story_aessop(state: AesopState) -> Dict[str, Any]:
    """
    Generates the final story based on analysis and brainstorming
    """
    logger.info("== Aesop Subgraph: Generate Story ==")
    original_fable = state.get("original_fable", "")
    analysis = state.get("analysis", {})
    brainstorm = state.get("brainstorm", {})
    
    logger.info(f"Generating story based on analysis and brainstorming")
    
    response = openai_41_mini_client.invoke([
        SystemMessage(content=GENERATE_STORY_AESOP_PROMPT),
        HumanMessage(content=f"""
        Original fable: {original_fable}
        
        Analysis: {json.dumps(analysis, indent=2)}
        
        Brainstorming: {json.dumps(brainstorm, indent=2)}
        
        Create a refined version of this fable.
        """)
    ])
    
    generated_story = response.content
    logger.info(f"Story generated (length: {len(generated_story)} characters)")
    
    return {"generated_story": generated_story}

@track_node("human_verification", "aesop_tool")
def human_verification(state: AesopState) -> Dict[str, Any]:
    """
    Human Verification node with approval/refection and optioman Modifications
    """
    logger.info("== Aesop Subgraph: Human Verification ==")
    generated_story = state.get("generated_story", "")
    analysis = state.get("analysis", {})
    revision_count = state.get("revision_count", 0)


    verification_data = {
        "story_content": generated_story,
        "story_word_count": len(generated_story.split()),
        "moral": analysis.get("moral", ""),
        "characters": analysis.get("characters", []),
        "revision_count": revision_count,
        "request__type": "story_approval"
    }

    human_response = interrupt(verification_data)
    # Process human response
    if human_response.get("action") == "approve":
        logger.info("Story approved by human reviewer")
        return {
            "human_approved": True, 
            "feedback": human_response.get("feedback", "Approved")
        }
    
    elif human_response.get("action") == "reject":
        logger.info("Story rejected by human reviewer")
        return {
            "human_approved": False, 
            "feedback": human_response.get("feedback", ""),
            "revision_request": human_response.get("revision_notes", "Please improve the story"),
            "revision_count": revision_count + 1
        }
    
    else:
        # Default to rejection for safety
        logger.warning("No clear approval received, defaulting to rejection")
        return {
            "human_approved": False, 
            "feedback": "No clear approval received",
            "revision_request": "Please review and improve the story",
            "revision_count": revision_count + 1
        }

@track_node("revise_story", "aesop_tool")
def revise_story(state: AesopState) -> Dict[str, Any]:
    """
    Revises the story based on human feedback
    """

    logger.info("== Aesop Subgraph: Revise Story ==")

    original_story = state.get("generated_story", "")
    revision_request = state.get("revision_request", "")
    analysis = state.get("analysis", {})
    brainstorm = state.get("brainstorm", {})
    revision_count = state.get("revision_count", 0)


    system_prompt = GENERATE_STORY_AESOP_PROMPT + f"""
    
    IMPORTANT: This is a revision based on human feedback. 
    Human feedback: {revision_request}
    
    Please address the feedback while maintaining the core moral and structure.
    """

    user_prompt = f""" 
    Original story: {original_story}
    
    Human feedback: {revision_request}
    
    Analysis: {json.dumps(analysis, indent=2)}
    Brainstorming: {json.dumps(brainstorm, indent=2)}
    
    Please revise the story based on the human feedback while maintaining the core moral and structure.
    """

    response = openai_41_mini_client.invoke([
        SystemMessage(content = system_prompt),
        HumanMessage(content = user_prompt)
    ])

    # Track the llm revision
    track_llm_call(
        node_name = "revise_story",
        tool_name = "aesop_tool",
        model = "gpt-4.1-mini",
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        response_text=response.content
    )

    revise_story = response.content
    logger.info(f"Story Revised ({len(revise_story)}) characters")
    return {"generated_story": revise_story}

@track_node("image_prompt_generator", "aesop_tool")
def image_prompt_generator(state: AesopState) -> Dict[str, Any]:
    """
    Generates image prompts for key scenes in the story
    """
    logger.info("== Aesop Subgraph: Image Prompt Generator ==")
    generated_story = state.get("generated_story", "")
    analysis = state.get("analysis", {})
    
    # Create prompt for generating image descriptions
    system_prompt = IMAGE_PROMPT_GENERATOR_PROMPT
    
    user_prompt = f"""Story to visualize:
    {generated_story}

    Character information from analysis:
    {json.dumps(analysis.get('characters', {}), indent=2)}

    Generate 6-8 image prompts for key visual moments throughout this story."""
    
    # Call LLM to generate image prompts
    response = openai_41_mini_client.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ])
    
    # Track LLM call
    track_llm_call(
        node_name="image_prompt_generator",
        tool_name="aesop_tool",
        model="gpt-4.1-mini",
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        response_text=response.content
    )
    
    # FIXED PARSING: Extract individual scenes properly
    image_prompts_text = response.content
    image_prompts = []
    
    # Split by "SCENE " and process each section
    scenes_raw = image_prompts_text.split("SCENE ")[1:]  # Skip empty first element
    logger.info(f"DEBUG: Found {len(scenes_raw)} raw scene sections")
    
    for i, scene_text in enumerate(scenes_raw):
        lines = scene_text.strip().split('\n')
        if not lines:
            continue
            
        # First line: "1: Title" or "1: Title  "
        first_line = lines[0].strip()
        
        # Extract scene number and title
        if ':' in first_line:
            scene_num_part, title_part = first_line.split(':', 1)
            scene_number = int(scene_num_part.strip()) if scene_num_part.strip().isdigit() else i + 1
            title = title_part.strip()
        else:
            scene_number = i + 1
            title = first_line
        
        # Extract description (everything after the first line)
        description_lines = lines[1:] if len(lines) > 1 else []
        description = '\n'.join(description_lines).strip()
        
        image_prompts.append({
            "scene_number": scene_number,
            "title": title,
            "description": description,
            "story_part": 1 if scene_number <= len(scenes_raw)//2 else 2
        })
        
        logger.info(f"DEBUG: Parsed scene {scene_number}: '{title}' ({len(description)} chars)")
    
    logger.info(f"Generated {len(image_prompts)} image prompts")
    
    # Add to metadata tracker 
    if "current_story" in metadata and metadata["current_story"] in metadata["stories"]:
        story_id = metadata["current_story"]
        metadata["stories"][story_id]["image_prompts"] = {
            "count": len(image_prompts),
            "prompts": image_prompts,
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        logger.info("Added image prompts to metadata")
    
    return {"image_prompts": image_prompts}


def should_continue_after_verification(state: AesopState) -> Literal["approved", "revise_story"]:
    """
    Route based on human approval
    """
    human_approved = state.get("human_approved", False)
    revision_count = state.get("revision_count", 0)
    
    if human_approved:
        logger.info("Story approved - proceeding to image prompt generation")
        return "approved"  # ✓ Changed from "image_prompt_generator" to "approved"
    else:
        # Check revision count to prevent infinite loops
        if revision_count < 3:  # Max 3 revision attempts
            logger.info(f"Story rejected - proceeding to revision #{revision_count}")
            return "revise_story"
        else:
            # Force approval after max revisions
            logger.warning("Max revisions reached, proceeding to image generation")
            return "approved"  # ✓ Changed from "image_prompt_generator" to "approved"

# Cell 8: BUILD THE AESOP SUBGRAPH
def build_aesop_subgraph():
    """
    Builds the Aesop tool subgraph
    """
    builder = StateGraph(AesopState)
    
    # Add nodes
    builder.add_node("analyze_fable", analyze_fable)
    builder.add_node("brainstorm_story", brainstorm_story)
    builder.add_node("generate_story_aessop", generate_story_aessop)
    builder.add_node("human_verification", human_verification)
    builder.add_node("revise_story", revise_story)
    builder.add_node("image_prompt_generator", image_prompt_generator)
    
    # Add edges
    builder.add_edge(START, "analyze_fable")
    builder.add_edge("analyze_fable", "brainstorm_story")
    builder.add_edge("brainstorm_story", "generate_story_aessop")
    builder.add_edge("generate_story_aessop", "human_verification")
    
    # Fixed conditional edge mapping
    builder.add_conditional_edges(
        "human_verification",
        should_continue_after_verification,
        {
            "approved": "image_prompt_generator",        # Clear mapping: approved → end subgraph
            "revise_story": "revise_story"  # rejected → revise
        }
    )
    
    # After revision, go back to human verification
    builder.add_edge("revise_story", "human_verification")
    builder.add_edge("image_prompt_generator", END)

    graph = builder.compile()

    # # # Generate the graph
    # graph.get_graph().draw_mermaid_png(
    #         output_file_path="./graphs_images/aesop_subgraph.png",
    #         background_color="white",
    #         padding=10
    #     )

    # Compile
    return graph

# Cell 9: AESOP SUBGRAPH WRAPPER
def aesop_subgraph(processing_request: Dict) -> Dict:
    """
    Wrapper function that runs the Aesop subgraph
    """
    logger.info("=== Running Aesop Subgraph ===")
    
    # Create initial state for Aesop subgraph
    initial_state = {
        "original_fable": processing_request.get("fable_text", ""),
        "analysis": {},
        "brainstorm": {},
        "generated_story": "",
        "human_approved": False,
        "feedback": "",
        "revision_request": "",
        "revision_count": 0,
        "image_prompts": []
    }
    
    # Build and run the subgraph
    aesop_graph = build_aesop_subgraph()
    result = aesop_graph.invoke(initial_state)
    # DEBUG: Check what the subgraph returned
    logger.info(f"DEBUG: Aesop subgraph result keys: {list(result.keys())}")
    image_prompts_from_result = result.get("image_prompts", [])
    logger.info(f"DEBUG: Image prompts in subgraph result: {len(image_prompts_from_result)}")

    # Return the enriched state
    return {
        "analysis": result["analysis"],
        "brainstorm": result["brainstorm"],
        "generated_story": result["generated_story"],
        "human_approved": result.get("human_approved", False),
        "feedback": result.get("feedback", ""),
        "image_prompts": result.get("image_prompts", [])
    }
