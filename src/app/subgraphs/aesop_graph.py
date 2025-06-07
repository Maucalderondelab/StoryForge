from typing import Dict, List, Any, Optional, TypedDict
import json

# config import
from config.settings import AesopState
from config.models_settings import openai_41_mini_client, gemini_imagen3_client
from config.logger import logger

# langhfraph imports
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.runnables.graph import CurveStyle, MermaidDrawMethod, NodeStyles

# prompts import
from app.prompts.prompts import MAIN_AGENT_PROMPT, ANALYZE_FABLE_PROMPT, BRAINSTORM_STORY_PROMPT, GENERATE_STORY_AESOP_PROMPT, FORMAT_OUTPUT_PROMPT, IMAGE_PROMPT_GENERATOR_PROMPT

# import metadata tracker
from metadata_tracker.metadata_tracker import track_node, track_llm_call, metadata



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
    
    response = openai_41_mini_client.invoke([
        SystemMessage(content=BRAINSTORM_STORY_PROMPT),
        HumanMessage(content=f"Original fable: {original_fable}\n\nAnalysis: {json.dumps(analysis, indent=2)}")
    ])
    
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
    
    # Add edges
    builder.add_edge(START, "analyze_fable")
    builder.add_edge("analyze_fable", "brainstorm_story")
    builder.add_edge("brainstorm_story", "generate_story_aessop")
    builder.add_edge("generate_story_aessop", END)
    
    graph = builder.compile()

    # # Generate the graph
    # mermaid_graph = graph.get_graph().draw_mermaid_png(
    #     draw_method=MermaidDrawMethod.PYPPETEER,
    #     output_file_path="./graphs_images/aesop_subgraph.png"  # Specify where to save
    # )

    # Compile
    return builder.compile()

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
        "generated_story": ""
    }
    
    # Build and run the subgraph
    aesop_graph = build_aesop_subgraph()
    result = aesop_graph.invoke(initial_state)
    
    # Return the enriched state
    return {
        "analysis": result["analysis"],
        "brainstorm": result["brainstorm"],
        "generated_story": result["generated_story"]
    }
