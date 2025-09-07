import os
import logging
from flask import render_template, request, redirect, url_for, flash, jsonify, send_file
from app import app, db
from models import Comic, Panel, Character
from services.gemini_service import generate_comic_panel, edit_panel_with_instruction
from services.elevenlabs_service import generate_narration_audio
from utils.pdf_generator import create_comic_pdf

def generate_panel_title(scene_description):
    """Generate a short title from scene description"""
    # Extract first few meaningful words
    words = scene_description.split()
    
    # Remove common filler words
    meaningful_words = []
    filler_words = {'the', 'a', 'an', 'and', 'or', 'but', 'is', 'are', 'was', 'were', 'in', 'on', 'at', 'to', 'for', 'of'}
    
    for word in words[:8]:  # Take first 8 words max
        clean_word = word.strip('.,!?').lower()
        if clean_word not in filler_words and len(clean_word) > 2:
            meaningful_words.append(word.strip('.,!?').title())
        if len(meaningful_words) >= 4:  # Limit to 4 meaningful words
            break
    
    # If no meaningful words found, use first few words
    if not meaningful_words:
        meaningful_words = [word.strip('.,!?').title() for word in words[:3]]
    
    # Create title, max 50 characters
    title = ' '.join(meaningful_words)
    if len(title) > 50:
        title = title[:47] + '...'
    
    return title or "New Panel"

@app.route('/')
def index():
    """Main page - show recent comics and creation form"""
    recent_comics = Comic.query.order_by(Comic.updated_at.desc()).limit(5).all()
    return render_template('index.html', comics=recent_comics)

@app.route('/create', methods=['POST'])
def create_comic():
    """Create a new comic"""
    try:
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        style = request.form.get('style', 'realistic').strip()
        
        if not title:
            flash('Comic title is required', 'error')
            return redirect(url_for('index'))
        
        # Create new comic
        comic = Comic(
            title=title,
            description=description,
            style=style
        )
        db.session.add(comic)
        db.session.commit()
        
        flash(f'Comic "{title}" created successfully!', 'success')
        return redirect(url_for('edit_comic', comic_id=comic.id))
        
    except Exception as e:
        logging.error(f"Error creating comic: {e}")
        flash('Error creating comic. Please try again.', 'error')
        return redirect(url_for('index'))

@app.route('/comic/<int:comic_id>')
def view_comic(comic_id):
    """View a specific comic"""
    comic = Comic.query.get_or_404(comic_id)
    panels = Panel.query.filter_by(comic_id=comic_id).order_by(Panel.panel_number).all()
    return render_template('comic.html', comic=comic, panels=panels, view_mode=True)

@app.route('/comic/<int:comic_id>/edit')
def edit_comic(comic_id):
    """Edit a specific comic"""
    comic = Comic.query.get_or_404(comic_id)
    panels = Panel.query.filter_by(comic_id=comic_id).order_by(Panel.panel_number).all()
    return render_template('comic.html', comic=comic, panels=panels, view_mode=False)

@app.route('/comic/<int:comic_id>/add_character', methods=['POST'])
def add_character(comic_id):
    """Add a character to the comic"""
    try:
        comic = Comic.query.get_or_404(comic_id)
        
        name = request.form.get('character_name', '').strip()
        description = request.form.get('character_description', '').strip()
        
        if not name:
            flash('Character name is required', 'error')
            return redirect(url_for('edit_comic', comic_id=comic_id))
        
        # Get existing characters
        characters = comic.get_characters_dict()
        
        # Add new character
        characters[name] = {
            'description': description
        }
        
        # Save updated characters
        comic.set_characters_dict(characters)
        db.session.commit()
        
        flash(f'Character "{name}" added successfully!', 'success')
        return redirect(url_for('edit_comic', comic_id=comic_id))
        
    except Exception as e:
        logging.error(f"Error adding character: {e}")
        flash('Error adding character. Please try again.', 'error')
        return redirect(url_for('edit_comic', comic_id=comic_id))

    # Edit Character
@app.route('/comic/<int:comic_id>/edit_character/<character_name>', methods=['POST'])
def edit_character(comic_id, character_name):
        """Edit a character's details"""
        comic = Comic.query.get_or_404(comic_id)
        try:
            new_name = request.form.get('character_name', '').strip()
            description = request.form.get('character_description', '').strip()
            if not new_name:
                flash('Character name is required', 'error')
                return redirect(url_for('edit_comic', comic_id=comic_id))
            characters = comic.get_characters_dict()
            # Remove old entry if name changed
            if new_name != character_name and character_name in characters:
                characters.pop(character_name)
            characters[new_name] = {
                'description': description
            }
            comic.set_characters_dict(characters)
            db.session.commit()
            flash(f'Character "{new_name}" updated successfully!', 'success')
        except Exception as e:
            logging.error(f"Error editing character: {e}")
            flash('Error editing character. Please try again.', 'error')
        return redirect(url_for('edit_comic', comic_id=comic_id))

    # Delete Character
@app.route('/comic/<int:comic_id>/delete_character/<character_name>', methods=['POST'])
def delete_character(comic_id, character_name):
        """Delete a character from the comic"""
        comic = Comic.query.get_or_404(comic_id)
        try:
            characters = comic.get_characters_dict()
            if character_name in characters:
                characters.pop(character_name)
                comic.set_characters_dict(characters)
                db.session.commit()
                flash(f'Character "{character_name}" deleted.', 'success')
            else:
                flash('Character not found.', 'error')
        except Exception as e:
            logging.error(f"Error deleting character: {e}")
            flash('Error deleting character. Please try again.', 'error')
        return redirect(url_for('edit_comic', comic_id=comic_id))

@app.route('/comic/<int:comic_id>/generate_panel', methods=['POST'])
def generate_panel(comic_id):
    """Generate a new panel for the comic"""
    try:
        comic = Comic.query.get_or_404(comic_id)
        
        scene_description = request.form.get('scene_description', '').strip()
        narration_text = request.form.get('narration_text', '').strip()
        
        if not scene_description:
            flash('Scene description is required', 'error')
            return redirect(url_for('edit_comic', comic_id=comic_id))
        
        # Get next panel number
        last_panel = Panel.query.filter_by(comic_id=comic_id).order_by(Panel.panel_number.desc()).first()
        panel_number = (last_panel.panel_number + 1) if last_panel else 1
        
        # Generate the panel image
        characters = comic.get_characters_dict()
        image_path = generate_comic_panel(
            scene_description=scene_description,
            characters=characters,
            style=comic.style,
            panel_number=panel_number
        )
        
        if not image_path:
            flash('Failed to generate panel image. Please check your API key and try again.', 'error')
            return redirect(url_for('edit_comic', comic_id=comic_id))
        
        # Generate audio if narration is provided
        audio_path = None
        if narration_text:
            from services.elevenlabs_service import generate_narration_audio
            audio_path = generate_narration_audio(narration_text, panel_number)
            if not audio_path:
                flash('Panel generated successfully, but voice narration failed. You can add it later.', 'warning')
        
        # Generate panel title from scene description
        panel_title = generate_panel_title(scene_description)
        
        # Create panel record
        panel = Panel(
            comic_id=comic_id,
            panel_number=panel_number,
            title=panel_title,
            description=scene_description,
            image_path=image_path,
            narration_text=narration_text if narration_text else None,
            audio_path=audio_path
        )
        db.session.add(panel)
        db.session.commit()
        
        flash(f'Panel {panel_number} generated successfully!', 'success')
        return redirect(url_for('edit_comic', comic_id=comic_id))
        
    except Exception as e:
        logging.error(f"Error generating panel: {e}")
        flash('Error generating panel. Please try again.', 'error')
        return redirect(url_for('edit_comic', comic_id=comic_id))

@app.route('/panel/<int:panel_id>/edit', methods=['POST'])
def edit_panel(panel_id):
    """Edit an existing panel with natural language instructions"""
    try:
        panel = Panel.query.get_or_404(panel_id)
        edit_instruction = request.form.get('edit_instruction', '').strip()
        
        if not edit_instruction:
            flash('Edit instruction is required', 'error')
            return redirect(url_for('edit_comic', comic_id=panel.comic_id))
        
        # Get comic and characters for consistency
        comic = panel.comic
        characters = comic.get_characters_dict()
        
        # Edit the panel
        new_image_path = edit_panel_with_instruction(
            current_image_path=panel.image_path,
            edit_instruction=edit_instruction,
            original_description=panel.description,
            characters=characters,
            style=comic.style
        )
        
        if not new_image_path:
            flash('Failed to edit panel. Please try again.', 'error')
            return redirect(url_for('edit_comic', comic_id=panel.comic_id))
        
        # Update panel
        panel.image_path = new_image_path
        panel.description += f" [Edited: {edit_instruction}]"
        db.session.commit()
        
        flash('Panel edited successfully!', 'success')
        return redirect(url_for('edit_comic', comic_id=panel.comic_id))
        
    except Exception as e:
        logging.error(f"Error editing panel: {e}")
        flash('Error editing panel. Please try again.', 'error')
        return redirect(url_for('edit_comic', comic_id=panel.comic_id))

@app.route('/panel/<int:panel_id>/narrate', methods=['POST'])
def add_narration(panel_id):
    """Add narration to a panel"""
    try:
        panel = Panel.query.get_or_404(panel_id)
        narration_text = request.form.get('narration_text', '').strip()
        
        if not narration_text:
            flash('Narration text is required', 'error')
            return redirect(url_for('edit_comic', comic_id=panel.comic_id))
        
        # Generate audio
        audio_path = generate_narration_audio(narration_text, panel.id)
        
        # Update panel
        panel.narration_text = narration_text
        if audio_path:
            panel.audio_path = audio_path
        db.session.commit()
        
        flash('Narration added successfully!', 'success')
        return redirect(url_for('edit_comic', comic_id=panel.comic_id))
        
    except Exception as e:
        logging.error(f"Error adding narration: {e}")
        flash('Error adding narration. Please try again.', 'error')
        return redirect(url_for('edit_comic', comic_id=panel.comic_id))

@app.route('/comic/<int:comic_id>/export_pdf')
def export_pdf(comic_id):
    """Export comic as PDF"""
    try:
        comic = Comic.query.get_or_404(comic_id)
        panels = Panel.query.filter_by(comic_id=comic_id).order_by(Panel.panel_number).all()
        
        if not panels:
            flash('No panels to export', 'error')
            return redirect(url_for('view_comic', comic_id=comic_id))
        
        # Generate PDF
        pdf_path = create_comic_pdf(comic, panels)
        
        if not pdf_path or not os.path.exists(pdf_path):
            flash('Error creating PDF', 'error')
            return redirect(url_for('view_comic', comic_id=comic_id))
        
        return send_file(pdf_path, as_attachment=True, download_name=f"{comic.title}.pdf")
        
    except Exception as e:
        logging.error(f"Error exporting PDF: {e}")
        flash('Error exporting PDF. Please try again.', 'error')
        return redirect(url_for('view_comic', comic_id=comic_id))

@app.route('/panel/<int:panel_id>/delete', methods=['POST'])
def delete_panel(panel_id):
    """Delete a specific panel"""
    try:
        panel = Panel.query.get_or_404(panel_id)
        comic_id = panel.comic_id
        panel_number = panel.panel_number
        
        # Delete associated files
        if panel.image_path and os.path.exists(panel.image_path):
            os.remove(panel.image_path)
        if panel.audio_path and os.path.exists(panel.audio_path):
            os.remove(panel.audio_path)
        
        # Delete the panel from database
        db.session.delete(panel)
        db.session.commit()
        
        flash(f'Panel {panel_number} deleted successfully!', 'success')
        return redirect(url_for('edit_comic', comic_id=comic_id))
        
    except Exception as e:
        logging.error(f"Error deleting panel: {e}")
        flash('Error deleting panel. Please try again.', 'error')
        return redirect(url_for('index'))

@app.route('/delete_comic/<int:comic_id>', methods=['POST'])
def delete_comic(comic_id):
    """Delete a comic and all its panels"""
    try:
        comic = Comic.query.get_or_404(comic_id)
        
        # Delete associated files
        for panel in comic.panels:
            if panel.image_path and os.path.exists(panel.image_path):
                os.remove(panel.image_path)
            if panel.audio_path and os.path.exists(panel.audio_path):
                os.remove(panel.audio_path)
        
        db.session.delete(comic)
        db.session.commit()
        
        flash(f'Comic "{comic.title}" deleted successfully!', 'success')
        return redirect(url_for('index'))
        
    except Exception as e:
        logging.error(f"Error deleting comic: {e}")
        flash('Error deleting comic. Please try again.', 'error')
        return redirect(url_for('index'))

@app.errorhandler(404)
def not_found(error):
    return render_template('index.html', error="Page not found"), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('index.html', error="Internal server error"), 500
