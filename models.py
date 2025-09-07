from app import db
from datetime import datetime
import json

class Comic(db.Model):
    """Model for storing comic strips"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    style = db.Column(db.String(100))
    characters = db.Column(db.Text)  # JSON string of character data
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to panels
    panels = db.relationship('Panel', backref='comic', lazy=True, cascade='all, delete-orphan')
    
    def get_characters_dict(self):
        """Return characters as dictionary"""
        if self.characters:
            try:
                return json.loads(self.characters)
            except json.JSONDecodeError:
                return {}
        return {}
    
    def set_characters_dict(self, characters_dict):
        """Set characters from dictionary"""
        self.characters = json.dumps(characters_dict)

class Panel(db.Model):
    """Model for individual comic panels"""
    id = db.Column(db.Integer, primary_key=True)
    comic_id = db.Column(db.Integer, db.ForeignKey('comic.id'), nullable=False)
    panel_number = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(100))
    description = db.Column(db.Text, nullable=False)
    image_path = db.Column(db.String(500))
    narration_text = db.Column(db.Text)
    audio_path = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Panel {self.panel_number} of Comic {self.comic_id}>'

class Character(db.Model):
    """Model for storing character information"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    appearance = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Character {self.name}>'
