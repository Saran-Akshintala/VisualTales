import os
import logging
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from PIL import Image
from datetime import datetime

def create_comic_pdf(comic, panels):
    """
    Create a PDF from comic panels
    
    Args:
        comic: Comic model instance
        panels: List of Panel model instances
    
    Returns:
        str: Path to the generated PDF file, or None if failed
    """
    try:
        # Ensure exports directory exists
        os.makedirs("static/exports", exist_ok=True)
        
        # Generate PDF filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_title = "".join(c for c in comic.title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        pdf_path = f"static/exports/{safe_title}_{timestamp}.pdf"
        
        # Create PDF document
        doc = SimpleDocTemplate(pdf_path, pagesize=A4, 
                               rightMargin=72, leftMargin=72,
                               topMargin=72, bottomMargin=18)
        
        # Get styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor='black'
        )
        
        panel_title_style = ParagraphStyle(
            'PanelTitle',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=10,
            spaceBefore=20,
            alignment=TA_CENTER
        )
        
        description_style = ParagraphStyle(
            'Description',
            parent=styles['Normal'],
            fontSize=12,
            spaceAfter=15,
            alignment=TA_LEFT
        )
        
        # Build PDF content
        story = []
        
        # Add title
        story.append(Paragraph(comic.title, title_style))
        
        # Add comic description if available
        if comic.description:
            story.append(Paragraph(f"<i>{comic.description}</i>", description_style))
        
        story.append(Spacer(1, 20))
        
        # Add each panel
        for panel in panels:
            # Panel title - use descriptive title or fallback to panel number
            panel_title = panel.title if hasattr(panel, 'title') and panel.title else f"Panel {panel.panel_number}"
            story.append(Paragraph(panel_title, panel_title_style))
            
            # Add panel image if it exists
            if panel.image_path and os.path.exists(panel.image_path):
                try:
                    # Resize image to fit page
                    img = _resize_image_for_pdf(panel.image_path)
                    if img:
                        story.append(img)
                except Exception as e:
                    logging.error(f"Error adding image to PDF: {e}")
                    story.append(Paragraph(f"[Image not available: {panel.image_path}]", description_style))
            
            # Add scene description
            story.append(Paragraph(f"<b>Scene:</b> {panel.description}", description_style))
            
            # Add narration if available
            if panel.narration_text:
                story.append(Paragraph(f"<b>Narration:</b> {panel.narration_text}", description_style))
            
            # Add space between panels
            story.append(Spacer(1, 30))
        
        # Add creation date
        creation_date = comic.created_at.strftime("%B %d, %Y")
        story.append(Spacer(1, 50))
        story.append(Paragraph(f"<i>Created on {creation_date} with VisualTales</i>", 
                             ParagraphStyle('Footer', parent=styles['Normal'], 
                                          fontSize=10, alignment=TA_CENTER)))
        
        # Build PDF
        doc.build(story)
        logging.info(f"PDF created successfully: {pdf_path}")
        return pdf_path
        
    except Exception as e:
        logging.error(f"Error creating PDF: {e}")
        return None

def _resize_image_for_pdf(image_path, max_width=6*inch, max_height=4*inch):
    """
    Resize image to fit in PDF while maintaining aspect ratio
    
    Args:
        image_path (str): Path to the image file
        max_width (float): Maximum width in points
        max_height (float): Maximum height in points
    
    Returns:
        RLImage: ReportLab Image object, or None if failed
    """
    try:
        # Open image to get dimensions
        with Image.open(image_path) as img:
            img_width, img_height = img.size
        
        # Calculate scaling factor
        width_ratio = max_width / img_width
        height_ratio = max_height / img_height
        scale_factor = min(width_ratio, height_ratio)
        
        # Calculate new dimensions
        new_width = img_width * scale_factor
        new_height = img_height * scale_factor
        
        # Create ReportLab image
        rl_image = RLImage(image_path, width=new_width, height=new_height)
        return rl_image
        
    except Exception as e:
        logging.error(f"Error resizing image for PDF: {e}")
        return None

def create_character_sheet_pdf(comic):
    """
    Create a PDF with character descriptions
    
    Args:
        comic: Comic model instance with characters
    
    Returns:
        str: Path to the generated PDF file, or None if failed
    """
    try:
        characters = comic.get_characters_dict()
        if not characters:
            return None
        
        # Ensure exports directory exists
        os.makedirs("static/exports", exist_ok=True)
        
        # Generate PDF filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_title = "".join(c for c in comic.title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        pdf_path = f"static/exports/{safe_title}_characters_{timestamp}.pdf"
        
        # Create PDF document
        doc = SimpleDocTemplate(pdf_path, pagesize=A4)
        
        # Get styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=20,
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        char_name_style = ParagraphStyle(
            'CharName',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=10,
            spaceBefore=20
        )
        
        # Build PDF content
        story = []
        
        # Add title
        story.append(Paragraph(f"Character Sheet - {comic.title}", title_style))
        
        # Add each character
        for name, details in characters.items():
            story.append(Paragraph(name, char_name_style))
            
            if details.get('description'):
                story.append(Paragraph(f"<b>Description:</b> {details['description']}", styles['Normal']))
                story.append(Spacer(1, 10))
            
            if details.get('appearance'):
                story.append(Paragraph(f"<b>Appearance:</b> {details['appearance']}", styles['Normal']))
            
            story.append(Spacer(1, 20))
        
        # Build PDF
        doc.build(story)
        logging.info(f"Character sheet PDF created: {pdf_path}")
        return pdf_path
        
    except Exception as e:
        logging.error(f"Error creating character sheet PDF: {e}")
        return None
