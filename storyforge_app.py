import gradio as gr
import time
import re
import random
from pathlib import Path
import base64
import io
from PIL import Image as PILImage

# Import and create the workflow
from agents.storyteller import create_workflow

# Define the state type
from typing import TypedDict, Optional
from IPython.display import Image, display
from langchain_core.runnables.graph import CurveStyle, MermaidDrawMethod, NodeStyles

# Mock story data (replace with your LangGraph agent later)
SAMPLE_STORIES = {
"Moral & Reflection": {
        "title": "The Garden of Choices",
        "story": """In a small village nestled between rolling hills, there lived a gardener named Elara. Her garden was the most beautiful in the region, filled with flowers that seemed to dance with the wind and vegetables that tasted like they were kissed by the sun.

Many would visit Elara's garden to seek her wisdom, for it was said that she could provide guidance through the simple act of gardening. One day, a troubled young man named Thorne came to her garden.

"I stand at a crossroads," Thorne confessed, "and every path seems to lead to disappointment."

Elara smiled gently and handed him two seed packets. "Plant these in separate pots," she instructed. "Tend to the first with daily care—water, sunlight, and attention. Leave the second to fend for itself."

Weeks passed, and Thorne returned. The first pot displayed a vibrant, blooming flower, while the second contained only dry soil and a wilted sprout.

"Our lives are like these plants," Elara explained. "The paths we nurture with patience, dedication, and care will flourish. Those we neglect wither away. The choice isn't about which path to take, but which one deserves your devotion."

Thorne looked at the thriving plant, understanding dawning on his face. "So the disappointment comes not from the path itself, but from how I walk it."

Elara nodded. "The garden of life requires tending. Choose the seeds you plant carefully, but remember—your consistent care matters more than the initial choice."

Thorne left that day with both pots and a newfound clarity. The crossroads hadn't disappeared, but now he understood that whichever path he chose would be shaped by his commitment to it.""",
        "chapters": [
            {"time": "00:00", "title": "Introduction", "description": "The village and Elara's garden"},
            {"time": "01:30", "title": "Thorne's Dilemma", "description": "The young man at a crossroads"},
            {"time": "03:15", "title": "The Two Seeds", "description": "Elara's gardening lesson begins"},
            {"time": "05:00", "title": "The Results", "description": "What happened to each plant"},
            {"time": "06:45", "title": "The Lesson", "description": "The meaning behind the experiment"},
            {"time": "08:15", "title": "Resolution", "description": "Thorne's newfound understanding"}
        ]
    },
    "Historical": {
        "title": "The Silent Librarian of Alexandria",
        "story": """As flames licked the sky above the great Library of Alexandria in 48 BCE, Amara, a young Librarian's apprentice, moved with purpose through the smoke-filled halls. While Roman soldiers clashed with Egyptian forces outside, she had only one mission: to save as much knowledge as possible.

The Library housed over half a million scrolls—the greatest collection of knowledge in the ancient world. Philosophers, mathematicians, astronomers, and poets from across the Mediterranean had contributed to this temple of wisdom. And now it was burning.

Amara had studied under the great scholar Didymus for five years. "Knowledge preserved is a torch passed through generations," he had taught her. Tonight, those words drove her deeper into the burning building.

She knew the hidden vault beneath the main reading room—a secret chamber where the most precious documents were kept. The Astronomical treatises of Aristarchus suggesting Earth revolved around the sun. The anatomical studies of Herophilus. Mathematical works from Euclid and Archimedes. Maps charting lands beyond the known world.

Coughing through the thickening smoke, Amara reached the vault. The heat was becoming unbearable, but she methodically filled her leather satchels with the most irreplaceable scrolls. She couldn't save everything—choices had to be made about which knowledge would survive.

As the ceiling began to collapse, Amara escaped through a servant's passage carrying three heavy bags. She looked back once at the glowing building that had been her home and sanctuary.

History would remember the burning of the Library as an incalculable loss for humanity—thousands of scrolls and books destroyed, centuries of knowledge turned to ash. Few would know of Amara and the network of scholars who saved hundreds of texts, copying and distributing them throughout the ancient world.

The works she rescued that night would eventually find their way to Baghdad, Constantinople, and Damascus, preserving crucial knowledge that would otherwise have been lost forever. Amara herself would establish a small but significant library in Upper Egypt, becoming a silent guardian of the flame of knowledge that nearly went out on that terrible night in Alexandria.""",
        "chapters": [
            {"time": "00:00", "title": "Alexandria in Flames", "description": "The historical setting of 48 BCE"},
            {"time": "02:00", "title": "Amara's Mission", "description": "The apprentice's determination"},
            {"time": "04:15", "title": "The Great Library", "description": "Description of the world's knowledge center"},
            {"time": "06:30", "title": "The Secret Vault", "description": "Reaching the most precious documents"},
            {"time": "09:00", "title": "Difficult Choices", "description": "Deciding what knowledge to save"},
            {"time": "11:45", "title": "Escape", "description": "Fleeing the collapsing building"},
            {"time": "13:30", "title": "Legacy", "description": "How the rescued knowledge lived on"}
        ]
    },
    "Terror": {
        "title": "The Whispering House",
        "story": """The house on Blackwood Hill had been vacant for twenty years before Maya decided to purchase it. "It's just old," the real estate agent assured her when she noticed the goosebumps on her arms during the viewing. "These hillside homes creak a bit, that's all."

Maya loved the isolation and the view of the small town below. As a writer seeking quiet, it seemed perfect despite the rumors from locals about the previous owners' sudden, unexplained departure.

The first night, Maya convinced herself the whispers were just wind threading through the old walls. By the third night, she could almost distinguish words in the gentle, persistent murmuring that seemed to follow her from room to room.

"Just settling sounds," she told herself, setting up her writing desk by the bay window of the master bedroom. The words flowed easily here—too easily, sometimes appearing on her screen when she was certain she hadn't typed them.

One morning, Maya found a journal hidden behind a loose baseboard. The handwriting inside matched the strange sentences that had been appearing in her manuscript:

"They're in the walls now. They whisper their stories and beg me to write them. They need to be remembered. They need to be released."

The entries grew more frantic with each page until they stopped abruptly mid-sentence. That night, the whispers grew louder, and Maya realized they were coming from inside the walls—dozens of voices, overlapping, pleading.

When she pressed her ear against the faded wallpaper, it felt warm, almost like skin. Through a crack, she glimpsed something moving within the wall—not mice or insects, but something flowing, like ink forming words.

That night, Maya couldn't sleep. Her computer turned on by itself, cursor blinking expectantly. The whispers had become a chorus, impossible to ignore. "Write for us," they seemed to say. "Give us voice. Make us real again."

Exhausted, Maya sat at her desk and began to type. The words weren't hers, but they flowed through her fingers. With each paragraph, the whispers grew more satisfied, and the walls of the house seemed to pulse with anticipation.

By dawn, Maya had completed an entire manuscript—stories of lives cut short, of secrets buried, of things that happened in this house on Blackwood Hill over generations. As she typed the final period, the whispers finally ceased.

In the sudden silence, Maya heard a new sound—the gentle shifting of the walls around her, closing in inch by inch. She realized too late what the previous owner had discovered: the house didn't want a caretaker.

It wanted an author.""",
        "chapters": [
            {"time": "00:00", "title": "The House on Blackwood Hill", "description": "Introduction to the setting"},
            {"time": "01:45", "title": "First Nights", "description": "Maya begins to hear whispers"},
            {"time": "03:30", "title": "Strange Writing", "description": "Unexplained text appears in her work"},
            {"time": "05:15", "title": "The Hidden Journal", "description": "Discovery of the previous owner's writings"},
            {"time": "07:00", "title": "Voices in the Walls", "description": "The whispers intensify"},
            {"time": "09:30", "title": "Something Moving", "description": "Maya sees something inside the walls"},
            {"time": "11:15", "title": "The Bargain", "description": "Maya begins writing for the voices"},
            {"time": "13:45", "title": "Dawn Realization", "description": "The terrible truth about the house"}
        ]
    }
}

# Mock functions to simulate your LangGraph agent
def generate_story(prompt, story_type, length, style):
    """Simulate story generation (will be replaced with LangGraph agent call)"""
    # In a real implementation, this would call your LangGraph agent
    time.sleep(2)  # Simulate processing time
    
    # Just return the appropriate sample story for now
    story_data = SAMPLE_STORIES[story_type]
    return story_data["title"], story_data["story"], story_data["chapters"]

def convert_to_script_format(story):
    """Convert narrative text to script format for easy voiceover"""
    if not story:
        return ""
        
    # Split into paragraphs
    paragraphs = story.split('\n\n')
    script = ""
    
    for i, para in enumerate(paragraphs):
        script += f"[SECTION {i+1}]\n"
        # Add breathing pauses with double slashes
        para_with_pauses = re.sub(r'([.!?]) ', r'\1 // ', para)
        # Add emphasis to key phrases (simple implementation)
        words = para_with_pauses.split()
        for j in range(len(words)):
            # Randomly emphasize about 5% of words that are longer than 4 letters
            if len(words[j]) > 4 and random.random() < 0.05:
                words[j] = f"*{words[j]}*"
        
        enhanced_para = ' '.join(words)
        script += enhanced_para + "\n\n"
        
    script += "[END NARRATION]"
    return script

def generate_audio(title, story):
    """Simulate audio generation"""
    # This would call your audio generation service
    time.sleep(2)  # Simulate processing
    return "Audio generated successfully! Your voiceover is ready to download."

def format_youtube_chapters(chapters):
    """Format chapters for YouTube description"""
    # Format chapters for YouTube description
    result = "CHAPTERS:\n"
    for chapter in chapters:
        result += f"{chapter['time']} - {chapter['title']}\n"
    return result

# Create the Gradio interface
with gr.Blocks(theme=gr.themes.Soft(primary_hue="gray")) as demo:
    # Header
    gr.Markdown("# StoryForge")
    gr.Markdown("#### AI Storyteller for YouTube Content Creation")
    
    # Story type selection
    with gr.Row():
        story_type = gr.Radio(
            ["Moral & Reflection", "Historical", "Terror"],
            label="Select Story Type",
            value="Moral & Reflection"
        )
    
    # Main content area
    with gr.Tabs():
        # Story Generation Tab
        with gr.TabItem("Create Story"):
            with gr.Row():
                # Left panel - Input
                with gr.Column(scale=1):
                    prompt = gr.Textbox(
                        placeholder="What would you like a story about?",
                        label="Story Prompt",
                        lines=5
                    )
                    
                    with gr.Row():
                        length = gr.Radio(
                            ["Short", "Medium", "Long"],
                            label="Story Length",
                            value="Medium"
                        )
                    
                    style = gr.Dropdown(
                        ["Classic storytelling", "Modern", "Poetic", "Conversational"],
                        label="Style",
                        value="Classic storytelling"
                    )
                    
                    generate_btn = gr.Button("Generate Story", variant="primary")
                
                # Right panel - Output
                with gr.Column(scale=1):
                    with gr.Row():
                        title_output = gr.Textbox(label="Title")
                        format_toggle = gr.Radio(
                            ["Story", "Script"], 
                            label="Format", 
                            value="Story",
                            interactive=True
                        )
                    
                    # Two different text outputs for story/script format
                    with gr.Group():
                        story_output = gr.Textbox(label="Story", lines=12)
                        script_output = gr.Textbox(label="Script Format", lines=12, visible=False)
        ## Create a tah to visualize the worflow application
        with gr.TabItem("Agent Workflow"):
            gr.Markdown("### Story Agent Workflow")
            gr.Markdown("This tab shows how the story generation agent routes request the routes based on the story type")

            #Add a button to generate/refresh the visualization
            with gr.Row():
                visualize_btn = gr.Button("Generate/Refresh Workflow Diagram", variant="primary")
            
            # Add an image component to display the workflow diagram
            with gr.Row():
                workflow_image = gr.Image(
                    label="LangGraph Workflow", 
                    show_label=True,
                    interactive=False,
                    height=500
                )
            
            # Add explanatory text about the workflow
            with gr.Row():
                workflow_explanation = gr.Markdown("""
                **How the StoryForge Agent Works:**
                
                1. The workflow starts by taking your story parameters from the UI
                2. Based on the selected story type, it routes to the appropriate generation path
                3. Each story type has specialized prompting and generation strategies
                4. The completed story is returned to the UI for display
                
                This visualization helps you understand how LangGraph orchestrates the story generation process.
                """)
       ## Audio Generation Tab
       # with gr.TabItem("Audio"):
       #     with gr.Row():
       #         with gr.Column(scale=1):
       #             gr.Markdown("### Generate Voiceover")
       #             gr.Markdown("Convert your story into a professional voiceover for your YouTube video.")
       #             
       #             voice_type = gr.Dropdown(
       #                 ["Male - Deep", "Male - Neutral", "Female - Warm", "Female - Professional", "Child"],
       #                 label="Voice Type",
       #                 value="Male - Neutral"
       #             )
       #             
       #             audio_btn = gr.Button("🔊 Generate Audio", variant="primary")
       #             audio_status = gr.Textbox(label="Status", visible=True)
       #             
       #         with gr.Column(scale=1):
       #             audio_output = gr.Audio(label="Preview Audio", interactive=False, visible=False)
       #             download_btn = gr.Button("Download Audio", visible=False)
       # 
       # # Images Tab
       # with gr.TabItem("Images"):
       #     gr.Markdown("### Story Visualizations")
       #     gr.Markdown("Generate images based on key moments in your story for your YouTube video.")
       #     
       #     with gr.Row():
       #         image_prompt = gr.Textbox(label="Image Description (or leave empty to auto-generate)", lines=2)
       #         image_style = gr.Dropdown(
       #             ["Realistic", "Artistic", "Fantasy", "Sketch", "Cinematic"],
       #             label="Image Style",
       #             value="Cinematic"
       #         )
       #     
       #     generate_img_btn = gr.Button("Generate Images", variant="primary")
       #     
       #     with gr.Row():
       #         image_gallery = gr.Gallery(
       #             label="Generated Images",
       #             show_label=True,
       #             columns=3,
       #             height="250px",
       #             object_fit="contain"
       #         )
       # 
       # # YouTube Chapters Tab
       # with gr.TabItem("YouTube Chapters"):
       #     gr.Markdown("### Chapter Markers")
       #     gr.Markdown("Create timestamps for your YouTube video to improve navigation and engagement.")
       #     chapter_df = gr.Dataframe( headers=["Time", "Title", "Description"], datatype=["str", "str", "str"],
       #         row_count=5,
       #         col_count=(3, "fixed"),
       #         interactive=True
       #     )
       #     
       #     with gr.Row():
       #         add_chapter_btn = gr.Button("Add Chapter")
       #         export_chapters_btn = gr.Button("Export for YouTube")
       #     
       #     youtube_format = gr.Textbox(
       #         label="YouTube Description Format", 
       #         lines=8,
       #         interactive=False
       #     )
       # 
       # # Export Tab
       # with gr.TabItem("Export"):
       #     gr.Markdown("### Export Your Content")
       #     gr.Markdown("Download all assets for your YouTube video creation.")
       #     
       #     with gr.Row():
       #         with gr.Column(scale=1):
       #             gr.Markdown("#### Available Assets")
       #             export_checklist = gr.CheckboxGroup(
       #                 ["Story Text", "Script Format", "Audio Narration", "Generated Images", "Chapter Markers"],
       #                 label="Select Assets to Export"
       #             )
       #             export_format = gr.Radio(
       #                 ["Individual Files", "ZIP Package"],
       #                 label="Export Format",
       #                 value="ZIP Package"
       #             )
       #             export_all_btn = gr.Button("Export Selected Assets", variant="primary")
       #         
       #         with gr.Column(scale=1):
       #             export_status = gr.Textbox(label="Export Status")
       #             download_link = gr.File(label="Download", visible=False)
    # Set up event handlers
    def handle_story_generation(prompt, story_type, length, style):
        try:
            # Create the initial state with the UI inputs
            initial_state = {
                "prompt": prompt,
                "story_type": story_type,
                "length": length,
                "style": style,
                "title": "",  # Will be filled during generation
                "story": ""   # Will be filled during generation
            }
            
            
            class StoryState(TypedDict):
                prompt: str
                story_type: str
                length: str
                style: str
                title: Optional[str]
                story: Optional[str]

            print("Tried just before the workflow generation")
            # Create and execute the workflow
            workflow = create_workflow(StoryState)
            final_state = workflow.invoke(initial_state)
            
            # Return results
            return final_state.get("title", "Untitled"), final_state.get("story", "")

        except Exception as e:
            
            # Log the error
            print(f"Error generating story: {e}")
            # Fallback to sample stories
            story_data = SAMPLE_STORIES.get(story_type, SAMPLE_STORIES["Moral & Reflection"])
            return story_data["title"], story_data["story"]
    # Create a separate function for visualization
    def show_workflow():
        """
        Generates and displays the workflow diagram using Mermaid.Ink
        
        Returns:
            str: Path to the generated workflow image
        """
        diagram_path = "workflow_diagram.png"
        
        try:
            
            # Define the state type
            class StoryState(TypedDict):
                prompt: str
                story_type: str
                length: str
                style: str
                title: Optional[str]
                story: Optional[str]
            
            # Create the workflow (without invoking it)
            from agents.storyteller import create_workflow
            workflow = create_workflow(StoryState)
            
                        
    # Get the Mermaid diagram data
            mermaid_graph = workflow.get_graph().draw_mermaid_png(
                draw_method=MermaidDrawMethod.API
            )
            
            # The above returns the raw PNG data, so we need to save it
            # Convert base64 data to image and save
            if isinstance(mermaid_graph, bytes):
                # If it's raw bytes, save directly
                with open(diagram_path, "wb") as f:
                    f.write(mermaid_graph)
            elif isinstance(mermaid_graph, str) and mermaid_graph.startswith("data:image/png;base64,"):
                # If it's a base64 string, decode and save
                base64_data = mermaid_graph.split(",")[1]
                img_data = base64.b64decode(base64_data)
                with open(diagram_path, "wb") as f:
                    f.write(img_data)
            elif isinstance(mermaid_graph, str):
                # If it's mermaid code, use the Mermaid.Ink API
                mermaid_url = "https://mermaid.ink/img/"
                encoded_data = base64.b64encode(mermaid_graph.encode("utf-8")).decode("utf-8")
                response = requests.get(f"{mermaid_url}{encoded_data}")
                
                if response.status_code == 200:
                    with open(diagram_path, "wb") as f:
                        f.write(response.content)
                else:
                    print(f"Error from Mermaid.Ink API: {response.status_code}")
                    return None
            
            print(f"✓ Workflow diagram saved to {diagram_path}")
            return diagram_path
        
        except Exception as e:
            print(f"Error generating workflow diagram: {e}")
            import traceback
            traceback.print_exc()
            return None



    # Connect the button click to the handler function
    story_outputs = generate_btn.click(
        fn=handle_story_generation,
        inputs=[prompt, story_type, length, style],
        outputs=[title_output, story_output]
    )
    # Connect the visualization button to the handler
    visualize_btn.click(
        fn=show_workflow,
        outputs=workflow_image
    )
    # Handle format toggle
    def toggle_format(choice, story):
        if choice == "Story":
            return gr.update(visible=True), gr.update(visible=False)
        else:
            script = convert_to_script_format(story)
            return gr.update(visible=False), gr.update(visible=True, value=script)
    
    format_toggle.change(
        fn=toggle_format,
        inputs=[format_toggle, story_output],
        outputs=[story_output, script_output]
    )
    
   # # Audio generation
   # def handle_audio_gen():
   #     time.sleep(2)  # Simulate processing
   #     return gr.update(value="Audio generated successfully!"), gr.update(visible=True), gr.update(visible=True)
   # 
   # audio_btn.click(
   #     fn=handle_audio_gen,
   #     inputs=[],
   #     outputs=[audio_status, audio_output, download_btn]
   # )
   # 
   # # Format chapters for YouTube
   # export_chapters_btn.click(
   #     fn=format_youtube_chapters,
   #     inputs=[chapter_df],
   #     outputs=[youtube_format]
   # )
   # 
   # # Add a chapter row
   # def add_chapter_row(current_df):
   #     # This is a simplified version - in reality you'd need proper dataframe handling
   #     return current_df
   # 
   # add_chapter_btn.click(
   #     fn=add_chapter_row,
   #     inputs=[chapter_df],
   #     outputs=[chapter_df]
   # )
   # 
   # # Handle export
   # def handle_export(checklist):
   #     time.sleep(1)  # Simulate export process
   #     if not checklist:
   #         return "Please select at least one asset to export.", gr.update(visible=False)
   #     return f"Successfully exported: {', '.join(checklist)}", gr.update(visible=True)
   # 
   # export_all_btn.click(
   #     fn=handle_export,
   #     inputs=[export_checklist],
   #     outputs=[export_status, download_link]
   # )

# Launch the app
if __name__ == "__main__":
    demo.launch(share=True)
