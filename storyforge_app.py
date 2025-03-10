import gradio as gr
import time
import re
import random
from pathlib import Path
import base64
import io
import json
from PIL import Image as PILImage

# Import and create the workflow
from agents.storyteller import create_workflow

# Define the state type
from typing import TypedDict, Optional, Dict, List, Any
from IPython.display import Image, display
from langchain_core.runnables.graph import CurveStyle, MermaidDrawMethod, NodeStyles

# Mock story data (replace with your LangGraph agent later)
with open("SAMPLE_STORIES.json", "r") as f:
    SAMPLE_STORIES = json.load(f)

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
                "story": "",  # Will be filled during generation
                "iterations": 0,  # Add iteration tracking for our agents
                "sample_stories": SAMPLE_STORIES  # Add sample stories for fallback
            }
            
            # Define the state type - this should match the config.py StoryState
            class StoryState(TypedDict):
                prompt: str
                story_type: str
                length: str
                style: str
                title: Optional[str]
                story: Optional[str]
                iterations: Optional[int]
                sample_stories: Optional[Dict]
            
            print("🟩 Initial state:", initial_state)
            print("🟩 Creating workflow for story generation...")
            
            # Create and execute the workflow
            workflow = create_workflow(StoryState)
            print(f"🟩 Invoking workflow with prompt: {prompt[:300]}...")
            final_state = workflow.invoke(initial_state)
            
            # Return results
            return final_state.get("title", "Untitled"), final_state.get("story", "")

        except Exception as e:
            # Log the error
            print(f"🟥​Error generating story: {e}")
            import traceback
            traceback.print_exc()
            
            # Fallback to sample stories
            story_data = SAMPLE_STORIES.get(story_type, SAMPLE_STORIES["Moral & Reflection"])
            return story_data["title"], story_data["story"]
    # 2. Update the show_workflow function to ensure it captures the full workflow including our new branches
    # This updates the visualization part
    
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
                iterations: Optional[int]  # Add this for our historical branch
            
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
