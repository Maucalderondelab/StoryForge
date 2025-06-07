from app.graphs.main_graph import build_main_graph
from metadata_tracker.metadata_tracker import finish_story
from logging import getLogger
logger = getLogger(__name__)

def main():
    # Build the main graph
    main_graph = build_main_graph()
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
    
    # Run the graph
    result = main_graph.invoke(initial_state)
    
    # Print the results
    logger.info("=== FINAL STORY ===")
    logger.info(result["final_story"])
    
    logger.info("=== IMAGE PROMPTS ===")
    for prompt in result.get("image_prompts", []):
        logger.info(f"\nSCENE {prompt['scene_number']}")
        logger.info(prompt['description'])
    
    # Finish tracking this story
    story_stats = finish_story(result["final_story"])
    
    return result

if __name__ == "__main__":
    main()