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
        return {"tool_output": aesop_result}
    else:
        # Future: add more tool subgraphs
        logger.error(f"Tool not found")
        return {"tool_output": {"error": "Tool not found"}}
def parse_story_parts(story_text):
    """
    Parse the story into Part 1 and Part 2 sections
    """
    # Split on Part 2 marker
    if "**Part 2" in story_text:
        parts = story_text.split("**Part 2")
        
        # Clean Part 1
        part1_raw = parts[0]
        part1_clean = part1_raw.replace("**Part 1:**", "").replace("**Part 1**", "").strip()
        
        # Remove trailing "---" if present
        if part1_clean.endswith("---"):
            part1_clean = part1_clean[:-3].strip()
        
        # Clean Part 2
        part2_raw = "**Part 2" + parts[1] if len(parts) > 1 else ""
        
        # Split Part 2 to remove footer (everything after the last "---")
        part2_lines = part2_raw.split("---")
        if len(part2_lines) > 1:
            part2_clean = "---".join(part2_lines[:-1]).strip()  # Everything except last section
            footer = part2_lines[-1].strip()
        else:
            part2_clean = part2_raw.strip()
            footer = ""
        
        # Remove "**Part 2:**" or "**Part 2**" prefix from part2_clean
        part2_clean = part2_clean.replace("**Part 2:**", "").replace("**Part 2**", "").strip()
        
        return {
            "part_1": part1_clean,
            "part_2": part2_clean,
            "footer": footer,
            "full_story": story_text,
            "word_counts": {
                "part_1": len(part1_clean.split()),
                "part_2": len(part2_clean.split()),
                "total": len(story_text.split())
            }
        }
    else:
        # Fallback if no Part 2 found
        return {
            "part_1": story_text,
            "part_2": "",
            "footer": "",
            "full_story": story_text,
            "word_counts": {
                "part_1": len(story_text.split()),
                "part_2": 0,
                "total": len(story_text.split())
            }
        }
@track_node("generate_output", "main")
def generate_output(state: MainState) -> Dict[str, Any]:
    """
    Formats the final output based on the tool results
    Creates a two-part story with strict word count limits
    """
    logger.info("=== Generate Output ===")
    tool_output = state.get("tool_output", {})
    tool_name = state.get("tool_to_call", "")
    # DEBUG: Check tool_output contents
    logger.info(f"DEBUG: tool_output keys: {list(tool_output.keys())}")
    image_prompts = tool_output.get("image_prompts", [])
    logger.info(f"DEBUG: Image prompts in tool_output: {len(image_prompts)}")
    if "error" in tool_output:
        final_story = f"Error: {tool_output['error']}"
        logger.error(f"Error in tool output: {tool_output['error']}")
    else:
        if tool_name == "aesop_tool":
            # Get story components from the tool output
            generated_story = tool_output.get("generated_story", "")
            analysis = tool_output.get("analysis", {})
            brainstorm = tool_output.get("brainstorm", {})
            image_prompts = tool_output.get("image_prompts", [])

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
            story_parts = parse_story_parts(final_story)

            # Track final word count for metadata
            final_word_count = len(final_story.split())
            logger.info(f"Final story word count: {final_word_count}")
            
            # Verify the word counts of each part (for validation and debugging)
            parts = final_story.split("**Part 2")  # Added ** to match actual format
            if len(parts) > 1:
                part1 = parts[0].replace("**Part 1**", "").replace("**Part 1:**", "").strip()
                part2 = "**Part 2" + parts[1].strip()
                
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
                    
                    # Add parsed story parts
                    metadata["stories"][story_id]["story_parts"] = story_parts
                    
                    # Add image prompts to metadata
                    if image_prompts:
                        metadata["stories"][story_id]["image_prompts"] = {
                            "count": len(image_prompts),
                            "prompts": image_prompts,
                            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        }
                        logger.info(f"Added {len(image_prompts)} image prompts to metadata")
                    
                    logger.info("Added transformation and story parts metadata")
            else:
                # If no Part 2 found, still save the story_parts and image_prompts
                if "current_story" in metadata and metadata["current_story"] in metadata["stories"]:
                    story_id = metadata["current_story"]
                    metadata["stories"][story_id]["story_parts"] = story_parts
                    
                    if image_prompts:
                        metadata["stories"][story_id]["image_prompts"] = {
                            "count": len(image_prompts),
                            "prompts": image_prompts,
                            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        }
                    
                    logger.info("Added story_parts and image_prompts to metadata (fallback)")
        else:
            # Future: handle other tool outputs with different formatting strategies
            final_story = str(tool_output)
    
    return_data = {
        "final_story": final_story,
        "image_prompts": image_prompts
    }
    
    # DEBUG: Check what we're returning
    logger.info(f"DEBUG: generate_output returning {len(return_data['image_prompts'])} image prompts")
    
    return return_data
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

def build_main_graph(checkpointer = None):
    """
    Builds the main orchestrator graph with image prompt generation
    """
    builder = StateGraph(MainState)
    
    # Add nodes
    builder.add_node("main_agent", main_agent)
    builder.add_node("tool_router", tool_router)
    builder.add_node("generate_output", generate_output)
    
    # Add edges
    builder.add_edge(START, "main_agent")
    builder.add_edge("main_agent", "tool_router")
    builder.add_edge("tool_router", "generate_output")
    builder.add_edge("generate_output", END)
    
    # Compile
    graph = builder.compile(checkpointer=checkpointer)


    # # Generate the graph
    # graph.get_graph().draw_mermaid_png(
    #         output_file_path="./graphs_images/main_graph.png",
    #         background_color="white",
    #         padding=10
    #     )
    return graph
