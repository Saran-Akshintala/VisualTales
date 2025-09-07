# Overview

VisualTales is a Python Flask web application that enables users to create AI-powered comic strips with consistent characters, automated image generation, and voice narration. The application leverages Google's Gemini 2.5 Flash for image generation and ElevenLabs for text-to-speech functionality, providing an intuitive workflow for comic creation and export to PDF format.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Web Framework
- **Flask**: Lightweight Python web framework chosen for rapid development and simplicity
- **Flask-SQLAlchemy**: ORM integration for database operations with declarative models
- **SQLite**: Default database for local development with configurable DATABASE_URL for production
- **Jinja2 Templates**: Server-side rendering with Bootstrap dark theme for responsive UI

## Database Design
- **Comic Model**: Stores comic metadata (title, description, style) with JSON character definitions
- **Panel Model**: Individual comic panels with foreign key relationship to comics, including image paths and audio files
- **Character Model**: Standalone character definitions (currently defined but not actively used in favor of JSON storage)
- **Cascade Deletion**: Panels automatically deleted when parent comic is removed

## AI Service Integration
- **Gemini Service**: Handles image generation using Google's Gemini 2.5 Flash API with character consistency through prompt engineering
- **ElevenLabs Service**: Text-to-speech conversion for panel narration using Rachel voice model
- **Error Handling**: Graceful degradation when API keys are missing or services are unavailable

## File Management
- **Static Assets**: Images and audio files stored in static/ directory structure
- **PDF Export**: ReportLab integration for generating professional comic PDFs with embedded images and text
- **File Organization**: Timestamp-based naming for exports and generated content

## Frontend Architecture
- **Bootstrap 5**: Dark theme UI framework with Feather icons
- **Progressive Enhancement**: JavaScript adds interactivity while maintaining server-side functionality
- **Responsive Design**: Mobile-first approach with collapsible navigation and fluid layouts
- **AJAX Integration**: Panel generation and editing without full page reloads

## Security & Configuration
- **Environment Variables**: API keys and secrets stored in .env file
- **Session Management**: Flask sessions with configurable secret key
- **Input Validation**: Server-side validation for all user inputs
- **CSRF Protection**: Implicit through Flask's form handling

# External Dependencies

## AI Services
- **Google Gemini API**: Image generation service requiring GEMINI_API_KEY
- **ElevenLabs API**: Text-to-speech service requiring ELEVENLABS_API_KEY

## Python Packages
- **flask**: Web framework and routing
- **flask-sqlalchemy**: Database ORM and migrations
- **python-dotenv**: Environment variable management
- **requests**: HTTP client for external API calls
- **reportlab**: PDF generation and document creation
- **pillow**: Image processing and manipulation
- **google-genai**: Google Gemini API client library

## Frontend Libraries
- **Bootstrap 5**: CSS framework with dark theme variant
- **Feather Icons**: Lightweight icon library
- **Bootstrap JavaScript**: Interactive components and utilities

## Database
- **SQLite**: Default embedded database (configurable to PostgreSQL or other databases via DATABASE_URL)
- **SQLAlchemy**: Database abstraction layer with connection pooling