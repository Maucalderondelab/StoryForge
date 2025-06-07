import time
import json
import functools

from datetime import datetime
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

def track_llm_call(node_name, tool_name, model, system_prompt, user_prompt, response_text):
    """Track an LLM API call"""
    story_id = metadata.get("current_story")
    if not story_id:
        return
    
    # Simple token estimation (very rough)
    input_tokens = (len(system_prompt) + len(user_prompt)) // 4  # ~4 chars per token
    output_tokens = len(response_text) // 4
    
    # Cost estimation (very rough)
    if model == "gpt-4.1-mini":
        input_cost = (input_tokens / 1000) * 0.00040
        output_cost = (output_tokens / 1000) * 0.0016
    else:
        input_cost = (input_tokens / 1000) * 0.00010
        output_cost = (output_tokens / 1000) * 0.00030
    
    total_cost = input_cost + output_cost
    
    # Record the call
    call_data = {
        "timestamp": time.time(),
        "node": node_name,
        "tool": tool_name,
        "model": model,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": input_tokens + output_tokens,
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

def finish_story(output_text):
    """Finish tracking the current story"""
    story_id = metadata.get("current_story")
    if not story_id:
        return
    
    story = metadata["stories"][story_id]
    story["Generated Sttory"] = output_text
    story["end_time"] = time.time()
    story["duration"] = story["end_time"] - story["start_time"]
    story["output_length"] = len(output_text)
    
    # Calculate summary stats
    total_time = sum(node["total_time"] for node in story["nodes"].values())
    total_calls = sum(node["calls"] for node in story["nodes"].values())
    
    logger.info("=== STORY METRICS ===")
    logger.info(f"Total execution time: {story['duration']:.2f} seconds")
    logger.info(f"Total tokens: {story['total_tokens']} tokens")
    logger.info(f"Estimated cost: ${story['total_cost']:.4f}")
    logger.info(f"Number of nodes executed: {len(story['nodes'])}")
    logger.info(f"Number of LLM calls: {len(story['llm_calls'])}")
    
    # Reset current story
    metadata["current_story"] = None
    metadata["total_time"] += story["duration"]
    
    # Export metadata
    with open(f"story_metrics_{story_id}.json", "w") as f:
        json.dump(story, f, indent=2, default=str)
    
    logger.info(f"Metrics saved to story_metrics_{story_id}.json")
    
    return story