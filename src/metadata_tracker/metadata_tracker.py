import time
import json
import functools

from datetime import datetime
from pathlib import Path
import os

import tiktoken  # For token counting

from config.logger import logger

# Global metadata store
metadata = {
    "session_start": time.time(),
    "session_id": datetime.now().strftime("%Y%m%d_%H%M%S"),
    "current_story": None,
    "stories": {},
    "total_tokens": 0,
    "total_cost": 0,
    "total_time": 0
}

def track_node(node_name, tool_name="main"):
    """Decorator to track execution time of nodes"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(state):
            # Get current story ID or create one
            story_id = metadata.get("current_story")
            if not story_id:
                story_id = f"story_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                metadata["current_story"] = story_id
                metadata["stories"][story_id] = {
                    "start_time": time.time(),
                    "nodes": {},
                    "tools": {},
                    "llm_calls": [],
                    "total_tokens": 0,
                    "total_cost": 0
                }
            
            # Initialize node data if needed
            story = metadata["stories"][story_id]
            if node_name not in story["nodes"]:
                story["nodes"][node_name] = {
                    "calls": 0,
                    "total_time": 0,
                    "tokens": 0
                }
            
            # Start timing
            start_time = time.time()
            
            # Call the function
            try:
                result = func(state)
                # Record timing data
                end_time = time.time()
                duration = end_time - start_time
                
                # Update metrics
                story["nodes"][node_name]["calls"] += 1
                story["nodes"][node_name]["total_time"] += duration
                
                logger.info(f"Node {node_name} executed in {duration:.4f} seconds")
                
                return result
            except Exception as e:
                # Record error but re-raise
                end_time = time.time()
                duration = end_time - start_time
                
                logger.error(f"Error in {node_name}: {str(e)}")
                story["nodes"][node_name]["calls"] += 1
                story["nodes"][node_name]["total_time"] += duration
                story["nodes"][node_name]["errors"] = story["nodes"][node_name].get("errors", 0) + 1
                
                raise
        return wrapper
    return decorator

def track_llm_call(node_name, tool_name, model, system_prompt, user_prompt, response_text, cached_tokens=0):
    """Track an LLM API call"""
    story_id = metadata.get("current_story")
    if not story_id:
        return
    
    # Token estimation
    input_tokens = (len(system_prompt) + len(user_prompt)) // 4
    output_tokens = len(response_text) // 4
    
    # Cost estimation with current pricing
    if model == "gpt-4.1-mini":
        input_cost = (input_tokens / 1000) * 0.00015  # Current price
        cached_cost = (cached_tokens / 1000) * 0.000075  # 50% discount
        output_cost = (output_tokens / 1000) * 0.0006
    elif model == "o1-mini":  # Fixed model name
        input_cost = (input_tokens / 1000) * 0.003
        cached_cost = (cached_tokens / 1000) * 0.0015
        output_cost = (output_tokens / 1000) * 0.012
    else:
        input_cost = (input_tokens / 1000) * 0.0001
        cached_cost = 0
        output_cost = (output_tokens / 1000) * 0.0003
    
    total_cost = input_cost + output_cost + cached_cost
    
    # Record the call
    call_data = {
        "timestamp": time.time(),
        "node": node_name,
        "tool": tool_name,
        "model": model,
        "input_tokens": input_tokens,
        "cached_tokens": cached_tokens,
        "output_tokens": output_tokens,
        "total_tokens": input_tokens + output_tokens,
        "input_cost": input_cost,
        "cached_cost": cached_cost,
        "output_cost": output_cost,
        "total_cost": total_cost
    }
    
    # Update story
    story = metadata["stories"][story_id]
    story["llm_calls"].append(call_data)
    story["total_tokens"] += input_tokens + output_tokens
    story["total_cost"] += total_cost
    
    # Update node
    if node_name in story["nodes"]:
        story["nodes"][node_name]["tokens"] += input_tokens + output_tokens
    
    # Update global
    metadata["total_tokens"] += input_tokens + output_tokens
    metadata["total_cost"] += total_cost
    
    logger.info(f"LLM call in {node_name}: {input_tokens + output_tokens} tokens, ${total_cost:.4f}")
def track_image_generation(node_name, tool_name, model, prompt_text, num_images, image_specs=None):
    """Track image generation API calls"""
    story_id = metadata.get("current_story")
    if not story_id:
        return
    
    # Image generation costs
    if model == "imagen-3.0-generate-002":
        cost_per_image = 0.03  # Check current pricing
    else:
        cost_per_image = 0.02  # Fallback
    
    total_cost = num_images * cost_per_image
    
    # Record the call
    call_data = {
        "timestamp": time.time(),
        "node": node_name,
        "tool": tool_name,
        "model": model,
        "prompt_length": len(prompt_text),
        "num_images": num_images,
        "cost_per_image": cost_per_image,
        "total_cost": total_cost,
        "image_specs": image_specs or {}
    }
    
    # Update story
    story = metadata["stories"][story_id]
    if "image_calls" not in story:
        story["image_calls"] = []
    story["image_calls"].append(call_data)
    story["total_cost"] += total_cost
    
    logger.info(f"Image generation in {node_name}: {num_images} images, ${total_cost:.4f}")
def finish_story(output_text):
    """Finish tracking the current story with enhanced metrics"""
    story_id = metadata.get("current_story")
    if not story_id:
        return
    
    story = metadata["stories"][story_id]
    story["generated_story"] = output_text
    story["end_time"] = time.time()
    story["duration"] = story["end_time"] - story["start_time"]
    story["output_length"] = len(output_text)
    
    # Enhanced summary metrics
    story["summary"] = {
        "execution": {
            "total_duration": story["duration"],
            "node_count": len(story["nodes"]),
            "total_node_calls": sum(node["calls"] for node in story["nodes"].values())
        },
        "ai_usage": {
            "llm_calls": len(story["llm_calls"]),
            "total_tokens": story["total_tokens"],
            "total_cost": story["total_cost"],
            "image_calls": len(story.get("image_calls", [])),
            "total_image_cost": sum(call["total_cost"] for call in story.get("image_calls", []))
        },
        "content": {
            "input_length": len(story.get("input_fable", "")),
            "output_length": len(output_text),
            "word_count": len(output_text.split())
        }
    }
# Create the folder and save the story
    project_root = Path.cwd()
    base_dir = project_root / "./generated_stories"
    story_dir = base_dir / story_id
    story_dir.mkdir(parents=True, exist_ok=True)

    json_file_path = story_dir / "story_summary.json"
    with open(json_file_path, "w") as f:
        json.dump(story, f, indent=2, default=str)

    # Log enhanced metrics
    logger.info("=== ENHANCED STORY METRICS ===")
    logger.info(f"Duration: {story['duration']:.2f}s | Tokens: {story['total_tokens']} | Cost: ${story['total_cost']:.4f}")
    logger.info(f"Nodes: {len(story['nodes'])} | LLM calls: {len(story['llm_calls'])} | Words: {len(output_text.split())}")
    
    # Reset and export
    metadata["current_story"] = None
    metadata["total_time"] += story["duration"]
    
    logger.info(f"Enhanced metrics saved to {json_file_path}")
    return story