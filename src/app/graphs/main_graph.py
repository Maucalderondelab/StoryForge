import time
from typing import Dict, List, Any, Optional, TypedDict
from datetime import datetime

import json

# config import
from config.settings import MainState
from config.models_settings import openai_41_mini_client, gemini_imagen3_client
from config.logger import setup_logger

# subgraphs import
from app.subgraphs.aesop_graph import aesop_subgraph
# langhfraph imports
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.runnables.graph import CurveStyle, MermaidDrawMethod, NodeStyles

# prompts import
from app.prompts.prompts import FORMAT_OUTPUT_PROMPT, IMAGE_PROMPT_GENERATOR_PROMPT

# metadata tracker import
from metadata_tracker.metadata_tracker import track_node, track_llm_call, track_image_generation, metadata

logger = setup_logger()

@track_node("main_agent", "main")
def main_agent(state: MainState) -> Dict[str, Any]:
    """
    Main orchestrator that analyzes input and decides which tool to use
    """
    logger.info("=== Main Agent ===")
    current_fable = state.get("current_fable", "")
    messages = state.get("messages", [])
    
    user_message = messages[-1].get("content", "") if messages else ""
    logger.info(f"Processing request: {user_message}")
    logger.info(f"Current fable length: {len(current_fable)} characters")
    
    is_aesop = True
    
    if is_aesop:
        processing_request = {
            "user_intent": user_message,
            "fable_text": current_fable
        }
        
        result = {
            "processing_request": processing_request,
            "tool_to_call": "aesop_tool"
        }
        logger.info(f"Selecting tool: aesop_tool")
        time.sleep(1)
        return result
    else:
        # Future expansion for other tools
        logger.info(f"Selecting tool: generic_tool")
        return {
            "processing_request": {},
            "tool_to_call": "generic_tool" 
        }

# Cell 5: Tool Router
def tool_router(state: MainState) -> Dict[str, Any]:
    """
    Routes to the appropriate tool subgraph
    """
    logger.info("=== Tool Router ===")
    tool_name = state.get("tool_to_call", "")
    processing_request = state.get("processing_request", {})
    
    logger.info(f"Routing to tool: {tool_name}")
    
    if tool_name == "aesop_tool":
        # Call the Aesop subgraph
        aesop_result = aesop_subgraph(processing_request)
        logger.info(f"Received result from Aesop tool: {aesop_result}")
        return {"tool_output": aesop_result}
    else:
        # Future: add more tool subgraphs
        logger.error(f"Tool not found")
        return {"tool_output": {"error": "Tool not found"}}

@track_node("generate_output", "main")
def generate_output(state: MainState) -> Dict[str, Any]:
    """
    Formats the final output based on the tool results
    Creates a two-part story with strict word count limits
    """
    logger.info("=== Generate Output ===")
    tool_output = state.get("tool_output", {})
    tool_name = state.get("tool_to_call", "")
    
    if "error" in tool_output:
        final_story = f"Error: {tool_output['error']}"
        logger.error(f"Error in tool output: {tool_output['error']}")
    else:
        if tool_name == "aesop_tool":
            # Get story components from the tool output
            generated_story = tool_output.get("generated_story", "")
            analysis = tool_output.get("analysis", {})
            brainstorm = tool_output.get("brainstorm", {})
            
            # Track the original story length for metadata
            original_word_count = len(generated_story.split())
            logger.info(f"Original story word count: {original_word_count}")
            
            # Create a prompt to split and enhance the story with strict word counts
            system_prompt = FORMAT_OUTPUT_PROMPT
            
            user_prompt = f"""Story: {generated_story}
            
            Analysis: {json.dumps(analysis, indent=2)}
            
            Split this into a two-part story as described, with exactly 80 words maximum for each part.
            Ensure Part 2 begins with a brief recap so viewers can understand the conclusion even if they missed Part 1.
            """
            
            # Call LLM to reformat the story
            response = openai_41_mini_client.invoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ])
            
            # Track LLM call
            track_llm_call(
                node_name="generate_output",
                tool_name="main",
                model="gpt-4.1-mini",
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                response_text=response.content
            )
            
            # The final reformatted story
            final_story = response.content
            
            # Track final word count for metadata
            final_word_count = len(final_story.split())
            logger.info(f"Final story word count: {final_word_count}")
            
            # Verify the word counts of each part (for validation and debugging)
            parts = final_story.split("PART 2")
            if len(parts) > 1:
                part1 = parts[0].replace("PART 1", "").strip()
                part2 = "PART 2" + parts[1].strip()
                
                part1_words = len(part1.split())
                part2_words = len(part2.split())
                
                logger.info(f"Part 1 word count: {part1_words}")
                logger.info(f"Part 2 word count: {part2_words}")
                
                # Add to metadata
                if "current_story" in metadata and metadata["current_story"] in metadata["stories"]:
                    story_id = metadata["current_story"]
                    if "transformations" not in metadata["stories"][story_id]:
                        metadata["stories"][story_id]["transformations"] = {}
                    
                    metadata["stories"][story_id]["transformations"]["story_split"] = {
                        "original_word_count": original_word_count,
                        "final_word_count": final_word_count,
                        "part1_word_count": part1_words,
                        "part2_word_count": part2_words,
                        "transformation_type": "two-part-fixed-length",
                        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                    
                    logger.info("Added transformation metadata")
        else:
            # Future: handle other tool outputs with different formatting strategies
            final_story = str(tool_output)
    
    logger.info(f"Final story generated (length: {len(final_story)} characters)")
    return {"final_story": final_story}


@track_node("image_prompt_generator", "main")
def image_prompt_generator(state: MainState) -> Dict[str, Any]:
    """
    Generates image prompts for key scenes in the two-part story
    """
    logger.info("=== Image Prompt Generator ===")
    final_story = state.get("final_story", "")
    tool_output = state.get("tool_output", {})
    
    # Extract analysis for context
    analysis = tool_output.get("analysis", {})
    
    # Split the story into parts
    parts = final_story.split("PART 2")
    if len(parts) < 2:
        parts = [final_story, ""]  # Fallback if not properly split
    
    part1 = parts[0].replace("PART 1", "").strip()
    part2 = "PART 2" + parts[1].strip() if len(parts) > 1 else ""
    
    # Create prompt for generating image descriptions
    system_prompt = IMAGE_PROMPT_GENERATOR_PROMPT
    
    user_prompt = f"""Two-part fable to visualize:

    PART 1:
    {part1}

    PART 2:
    {part2}

    Character information from analysis:
    {json.dumps(analysis.get('characters', {}), indent=2)}

    Generate 8-10 image prompts for key visual moments throughout this story."""
    
    # Call LLM to generate image prompts
    response = openai_41_mini_client.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ])
    
    # Track LLM call
    track_image_generation(
        node_name="image_prompt_generator",
        tool_name="main",
        model="imagen-3.0-generate-002",
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        response_text=response.content
    )
    
    # Process the response into structured prompts
    image_prompts_text = response.content
    
    # Parse the scene prompts
    import re
    scene_pattern = r'SCENE (\d+): ([^\n]+)\n(.*?)(?=SCENE \d+:|$)'
    matches = re.findall(scene_pattern, image_prompts_text, re.DOTALL)
    
    image_prompts = []
    for scene_num, title, description in matches:
        image_prompts.append({
            "scene_number": int(scene_num),
            #"title": title.strip(),
            "description": description.strip(),
            "story_part": 1 if int(scene_num) <= len(matches)//2 else 2,  # Rough division between parts
        })
    
    # Add metadata
    if "current_story" in metadata and metadata["current_story"] in metadata["stories"]:
        story_id = metadata["current_story"]
        metadata["stories"][story_id]["image_prompts"] = {
            "count": len(image_prompts),
            "prompts": image_prompts,
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    logger.info(f"Generated {len(image_prompts)} image prompts")    
    # Return augmented state with image prompts
    return {"image_prompts": image_prompts}

# Cell 10: BUILD THE MAIN GRAPH
def decide_next_step(state: MainState) -> str:
    """
    Decide whether to generate image prompts based on tool type
    """
    tool_name = state.get("tool_to_call", "")
    
    if tool_name == "aesop_tool":
        return "image_prompt_generator"
    else:
        return END

def build_main_graph():
    """
    Builds the main orchestrator graph with image prompt generation
    """
    builder = StateGraph(MainState)
    
    # Add nodes
    builder.add_node("main_agent", main_agent)
    builder.add_node("tool_router", tool_router)
    builder.add_node("generate_output", generate_output)
    builder.add_node("image_prompt_generator", image_prompt_generator)
    
    # Add edges
    builder.add_edge(START, "main_agent")
    builder.add_edge("main_agent", "tool_router")
    builder.add_edge("tool_router", "generate_output")
    
    # # Conditional edge after generate_output
    # builder.add_conditional_edges(
    #     "generate_output",
    #     decide_next_step,
    #     {
    #         "image_prompt_generator": "image_prompt_generator",
    #         END: END
    #     }
    # )
    
    # Final edgegenerate_output
    builder.add_edge("generate_output", END)
    # builder.add_edge("image_prompt_generator", END)
    
    # Compile
    graph = builder.compile()

    # # Generate the graph
    # mermaid_graph = graph.get_graph().draw_mermaid_png(
    #     draw_method=MermaidDrawMethod.PYPPETEER,
    #     output_file_path="./graphs_images/main_graph.png"  # Specify where to save
    # )

    return graph
