import time
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command
from app.graphs.main_graph import build_main_graph
from metadata_tracker.metadata_tracker import finish_story
from logging import getLogger
logger = getLogger(__name__)

def main():
    checkpointer = MemorySaver()
    # Build the main graph
    main_graph = build_main_graph(checkpointer)
    logger.info("Graph built successfully!")
    
    # Test with a sample Aesop fable
    test_fable = """
    La zorra y el perro.

    Penetró una zorra en un rebaño de corderos, y arrimando a su pecho
    a un pequeño corderillo, fingió acariciarle.

    Llegó un perro de los que cuidaban el rebaño y le preguntó:

    -- ¿Qué estás haciendo?

    -- Le acaricio y juego con él -- contestó con cara de inocencia.
    -- ¡ Pues suéltalo enseguida, si no quieres
    conocer mis mejores caricias!

    Al impreparado lo delatan sus actos.
    Estudia y aprende con gusto y tendrás

    éxito en tu vida.
    """
    
    initial_state = {
        "messages": [{"role": "user", "content": "Analyze and enhance this fable"}],
        "current_fable": test_fable,
        "tool_to_call": "",
        "processing_request": {},
        "tool_output": {},
        "final_story": "",
        "image_prompts": []
    }
    
    # Thread config (required for checkpointing/HIL)
    config = {"configurable": {"thread_id": f"story_{int(time.time())}"}}
    
    # === CHANGED EXECUTION PATTERN ===
    
    # Step 1: Run the graph - it might get interrupted
    result = main_graph.invoke(initial_state, config)

    # Step 2: Check if the graph was interrupted (HIL)
    while "__interrupt__" in result:
        # Extract the interruption data
        interrupt_data = result["__interrupt__"][0].value
        
        logger.info("=== HUMAN VERIFICATION REQUIRED ===")
        logger.info(f"Story to review:\n{interrupt_data['story_content']}")
        logger.info(f"Word count: {interrupt_data['story_word_count']}")
        logger.info(f"Moral: {interrupt_data['moral']}")
        
        # Get human input (CLI for now, later could be web interface)
        human_response = get_human_approval_cli(interrupt_data)
        
        # Resume the graph with human input
        result = main_graph.invoke(
            Command(resume=human_response), 
            config
        )
    
    # Step 3: Once no more interruptions, we have the final result
    # DEBUG: Check main graph result
    logger.info(f"DEBUG: Main graph result keys: {list(result.keys())}")
    image_prompts = result.get("image_prompts", [])
    logger.info(f"DEBUG: Image prompts in main result: {len(image_prompts)}")

    # Print the results
    logger.info("=== FINAL STORY ===")
    logger.info(result["final_story"])

    logger.info("=== IMAGE PROMPTS ===")
    for prompt in image_prompts:
        logger.info(f"\nSCENE {prompt['scene_number']}: {prompt.get('title', '')}")
        logger.info(prompt['description'][:100] + "..." if len(prompt['description']) > 100 else prompt['description'])

    # Finish tracking this story WITH image prompts
    story_stats = finish_story(result["final_story"], image_prompts)
    
    return result

def get_human_approval_cli(interrupt_data):
    """
    Simple CLI interface for human approval
    """
    print("\n" + "="*60)
    print("HUMAN VERIFICATION REQUIRED")
    print("="*60)
    print(f"Story Content:\n{interrupt_data['story_content']}")
    print(f"\nWord Count: {interrupt_data['story_word_count']}")
    print(f"Moral: {interrupt_data['moral']}")
    print("="*60)
    
    while True:
        decision = input("\nDo you approve this story? (approve/reject): ").lower().strip()
        
        if decision == "approve":
            feedback = input("Any feedback? (optional): ").strip()
            return {
                "action": "approve",
                "feedback": feedback
            }
        
        elif decision == "reject":
            revision_notes = input("What needs to be changed?: ").strip()
            return {
                "action": "reject", 
                "revision_notes": revision_notes,
                "feedback": f"Story rejected: {revision_notes}"
            }
        
        else:
            print("Please enter 'approve' or 'reject'")

if __name__ == "__main__":
    main()