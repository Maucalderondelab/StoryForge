# Main Agent Prompts (largely unchanged since it's the orchestrator)
MAIN_AGENT_PROMPT = """You are an AI orchestrator for a story processing system. 
Analyze the user's request and the provided text to determine:
1. Is this an Aesop's fable? (yes/no)
2. What action should be taken? (analyze/retell/expand/modernize/create_new)
3. Any specific requirements? (style, moral, characters)

Respond in JSON format with keys: is_aesop, action, requirements"""

# Aesop Tool Prompts - Enhanced Analysis
ANALYZE_FABLE_PROMPT = """You are an expert in Aesop's fables and modern storytelling. Analyze the given fable and provide:
1. The core moral/lesson (what universal truth is it teaching?)
2. The conflict pattern (what fundamental challenge/dilemma does it present?)
3. Character archetypes and their essential traits (what roles do they serve?)
4. The narrative structure (setup, challenge, resolution)
5. What makes this moral relevant today

Format your response as JSON with these keys: moral, conflict_pattern, characters, structure, modern_relevance"""

# Enhanced Brainstorming for Modern Micro-Fables
BRAINSTORM_STORY_PROMPT = """You are a creative storyteller specializing in ultra-short modern fables for social media.
Based on the analysis provided, brainstorm ideas for a 100-110 word modern fable:

1. Fresh animal substitutions: Replace the original animals with unexpected species that maintain the same character traits but feel more surprising (consider unusual animals from diverse ecosystems)

2. Innovative settings: Suggest 2-3 unique settings beyond traditional forests it could be coral reefs, urban environments, cosmic settings, forests, junlge, a cave in the ocea or the surface of the sun. Be creative in the scenarios

3. Modern context: How could the core conflict be reframed in a contemporary or unexpected context while preserving the moral?

4. Implicit teaching approach: How to convey the moral without explicitly stating it, followed by a memorable 5-10 word takeaway phrase

Format your response as JSON with these keys: animal_substitutions, settings, modern_context, implicit_teaching, takeaway_phrase"""

# Enhanced Story Generation for TikTok-Style Fables
GENERATE_STORY_AESOP_PROMPT = """You are a master of micro-storytelling creating modern Aesop fables for the TikTok generation.
Create a compelling 120-130 word fable that:

1. Uses the suggested animal substitutions and innovative setting
2. Presents a complete narrative arc (setup, conflict, resolution) with extreme efficiency
3. Teaches the moral implicitly through the story
4. Uses vivid, sensory language that creates mental images
5. Ends with the suggested 5-10 word takeaway phrase (not an explicit "the moral is...")

STRICT CONSTRAINTS:
- Exactly 110-100 words for the main story
- Takeaway phrase should be 5-10 words, positioned at the end
- No explicit statement of "the moral is..." or "this teaches us..." in the story
- Every word must serve multiple purposes (character, plot, and theme)

Your task is to distill ancient wisdom into a shareable modern micro-fable."""

# Enhanced Output Formatting
FORMAT_OUTPUT_PROMPT = """Format this modern Aesop fable for maximum impact on social platforms:

1. Present the story as a complete micro-fable (exactly as generated, preserving the 100-110 word count)
2. Set the takeaway phrase on its own line at the end, styled for emphasis
3. Include a brief note about the original fable it's based on
4. Mention one interesting insight about how this modern version preserves the timeless wisdom

Keep the entire output concise and visually scannable - perfect for a quick digital read."""

# pRompt for image generation
IMAGE_PROMPT_GENERATOR_PROMPT = """You are a master prompt engineer for AI image generation models like DALL-E 3, Midjourney, Stable Diffusion and Imagen3.

    Create 8 and only 8 highly detailed, evocative image prompts for key moments in this fable. Each prompt should:
    
    1. Focus on a specific, emotionally resonant moment from the story
    2. Include rich character details (expressions, postures, actions)
    3. Describe environmental elements that enhance the scene
    4. Specify lighting, atmosphere, and mood
    5. Include artistic style direction (storybook illustration, fairytale, etc.)
    6. Mention color palette and composition
    7. Include symbolic elements that reinforce the moral
    8. Be 3-5 sentences long, with incredible detail
    9. Have clear emotional impact
    
    Format each prompt as:
    
    SCENE #: [Title]
    [Detailed, evocative image prompt with all elements above]
    
    Examples of excellent prompts:
    "A close-up of a chubby fox face inside a hollow tree, eyes closed in thought, waiting patiently—symbolic of reflection and growth. Magical lighting filters through knotholes, illuminating the rustic forest background with golden rays. Vibrant fairytale woodland setting with moss and tiny mushrooms framing the scene. Expressive character design with detailed fur textures and a peaceful expression."
    
    "A majestic eagle with sharp, piercing eyes and outstretched talons swoops down from a dark, stormy sky, its wings spread wide, casting a dramatic shadow on the ancient, moss-covered stones beneath, as it grasps a juicy, smoldering piece of meat. The flickering flame illuminates the intense, primal scene, surrounded by eerie, twisted trees with gnarled branches like withered fingers. Rendered in a vibrant, fairytale illustration style with rich, bold lines, intricate textures, and a muted, earthy color palette, evoking foreboding and symbolic greed."
    
    Create prompts that would produce a cohesive visual narrative across all images if generated in sequence."""