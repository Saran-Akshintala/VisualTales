import os
import logging
import json
from datetime import datetime
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

# Read API key
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("❌ GEMINI_API_KEY not found. Please add it to your .env file.")

# Initialize Gemini client
client = genai.Client(api_key=api_key)


def generate_comic_panel(scene_description, characters, style="realistic", panel_number=1):
    """
    Generate a comic panel using Gemini 2.0 Flash Image Generation
    
    Args:
        scene_description (str): Description of the scene to generate
        characters (dict): Character definitions for consistency
        style (str): Art style for the comic
        panel_number (int): Panel number for file naming
    
    Returns:
        str: Path to the generated image file, or None if failed
    """
    try:
        # Create detailed character context only for mentioned characters
        character_context = ""
        if characters:
            # Extract character names mentioned in the scene description
            mentioned_characters = {}
            scene_lower = scene_description.lower()
            
            for name, details in characters.items():
                if name.lower() in scene_lower:
                    mentioned_characters[name] = details
            
            if mentioned_characters:
                character_context = "\nCHARACTER CONSISTENCY REQUIREMENTS:\n"
                for name, details in mentioned_characters.items():
                    desc = details.get('description', '')
                    character_context += f"- {name}: {desc}\n"
                character_context += "\nIMPORTANT: Maintain exact visual consistency for all named characters across panels.\n"
        
        # Construct the prompt for image generation optimized for Gemini 2.5 Flash Image Preview
        prompt = f"""
        Create a comic book panel in {style} style.
        
        SCENE DESCRIPTION: {scene_description}
        {character_context}
        VISUAL REQUIREMENTS:
        - Comic book panel format with clear black borders
        - Maintain consistent character appearance if characters are mentioned
        - {style} art style throughout
        - High quality detailed illustration
        - Professional comic book quality
        - Clear visual storytelling
        - Appropriate for all ages
        """
        
        logging.info(f"Generating panel {panel_number} with prompt: {prompt[:100]}...")
        
        # Ensure static directory exists
        os.makedirs("static/images", exist_ok=True)
        
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        image_path = f"static/images/panel_{panel_number}_{timestamp}.jpg"
        
        # Call Gemini image generation
        response = client.models.generate_content(
            model="gemini-2.5-flash-image-preview",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=['TEXT', 'IMAGE']
            )
        )
        
        if not response.candidates:
            logging.error("No candidates returned from Gemini")
            return None
        
        content = response.candidates[0].content
        if not content or not content.parts:
            logging.error("No content parts in response")
            return None
        
        # Save the generated image
        for part in content.parts:
            if part.inline_data and part.inline_data.data:
                with open(image_path, 'wb') as f:
                    f.write(part.inline_data.data)
                logging.info(f"Panel saved as {image_path}")
                return image_path
            elif part.text:
                logging.info(f"Generated description: {part.text}")
        
        logging.error("No image data found in response")
        return None
        
    except Exception as e:
        logging.error(f"Error generating panel: {e}")
        # Return a mock path for development if API fails
        if not os.environ.get("GEMINI_API_KEY"):
            logging.warning("No GEMINI_API_KEY found, using placeholder")
            return _create_placeholder_image(panel_number, scene_description)
        return None

def edit_panel_with_instruction(current_image_path, edit_instruction, original_description, characters=None, style="realistic"):
    """
    Edit an existing panel with natural language instructions
    
    Args:
        current_image_path (str): Path to current panel image
        edit_instruction (str): Natural language editing instruction
        original_description (str): Original scene description
        characters (dict): Character definitions for consistency
        style (str): Art style for the comic
    
    Returns:
        str: Path to the edited image file, or None if failed
    """
    try:
        # Create detailed character context for consistency
        character_context = ""
        if characters:
            character_context = "\nCHARACTER CONSISTENCY REQUIREMENTS:\n"
            for name, details in characters.items():
                desc = details.get('description', '')
                character_context += f"- {name}: {desc}\n"
            character_context += "\nIMPORTANT: Maintain exact visual consistency for all named characters.\n"
        
        # Construct editing prompt with character context
        prompt = f"""
        Create a modified comic book panel in {style} style based on this editing instruction: {edit_instruction}
        
        ORIGINAL SCENE: {original_description}
        {character_context}
        EDITING INSTRUCTION: {edit_instruction}
        
        VISUAL REQUIREMENTS:
        - Apply the requested changes while maintaining overall composition
        - Maintain exact character consistency if characters are present
        - Keep {style} art style throughout
        - Comic book panel format with clear black borders
        - High quality detailed illustration
        - Professional comic book quality
        """
        
        logging.info(f"Editing panel with instruction: {edit_instruction}")
        
        # Ensure static directory exists
        os.makedirs("static/images", exist_ok=True)
        
        # Generate new filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        new_image_path = f"static/images/edited_panel_{timestamp}.jpg"
        
        # Call Gemini for editing (using image generation since editing isn't directly supported)
        response = client.models.generate_content(
            model="gemini-2.5-flash-image-preview",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=['TEXT', 'IMAGE']
            )
        )
        
        if not response.candidates:
            return None
        
        content = response.candidates[0].content
        if not content or not content.parts:
            return None
        
        # Save the edited image
        for part in content.parts:
            if part.inline_data and part.inline_data.data:
                with open(new_image_path, 'wb') as f:
                    f.write(part.inline_data.data)
                logging.info(f"Edited panel saved as {new_image_path}")
                return new_image_path
        
        return None
        
    except Exception as e:
        logging.error(f"Error editing panel: {e}")
        return None

def _create_placeholder_image(panel_number, description):
    """Create a placeholder image when API is not available"""
    from PIL import Image, ImageDraw, ImageFont
    import textwrap
    
    try:
        # Create a simple placeholder image
        img = Image.new('RGB', (800, 600), color='lightgray')
        draw = ImageDraw.Draw(img)
        
        # Try to use a default font, fallback to basic if not available
        try:
            font = ImageFont.truetype("arial.ttf", 24)
            small_font = ImageFont.truetype("arial.ttf", 16)
        except:
            font = ImageFont.load_default()
            small_font = font
        
        # Draw panel border
        draw.rectangle([10, 10, 790, 590], outline='black', width=3)
        
        # Draw title
        draw.text((50, 50), f"Panel {panel_number}", fill='black', font=font)
        
        # Draw description (wrapped)
        wrapped_text = textwrap.fill(description, width=60)
        draw.text((50, 100), wrapped_text, fill='black', font=small_font)
        
        # Draw placeholder text
        draw.text((50, 400), "Placeholder Image", fill='gray', font=font)
        draw.text((50, 450), "(Add GEMINI_API_KEY to generate real images)", fill='gray', font=small_font)
        
        # Save placeholder
        os.makedirs("static/images", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        placeholder_path = f"static/images/placeholder_{panel_number}_{timestamp}.jpg"
        img.save(placeholder_path)
        
        return placeholder_path
        
    except Exception as e:
        logging.error(f"Error creating placeholder image: {e}")
        return None
