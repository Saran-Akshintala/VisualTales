# VisualTales - AI-Powered Comic Studio

VisualTales is a Python Flask web application that lets you create stunning comic strips using AI-powered image generation and voice narration. Create consistent characters, generate comic panels, edit them with natural language instructions, and export your comics as PDFs.

## ✨ Features

- **AI Image Generation**: Create comic panels using Gemini 2.5 Flash Image API
- **Character Consistency**: Define characters once and maintain them across all panels
- **Natural Language Editing**: Edit panels with simple text instructions like "make it nighttime"
- **Voice Narration**: Add AI-generated voice narration using ElevenLabs TTS
- **PDF Export**: Export your complete comics as professional PDFs
- **Responsive Design**: Clean, modern web interface that works on all devices
- **Easy to Use**: Intuitive workflow for creating professional-looking comics

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Clone or download the project files**

2. **Install dependencies**:
   ```bash
   pip install flask flask-sqlalchemy python-dotenv requests reportlab pillow google-genai
   ```

3. **Set up environment variables**:
   ```bash
   cp .env.example .env
   ```
   
   Edit the `.env` file and add your API keys:
   ```bash
   SESSION_SECRET=your_random_secret_key_here
   GEMINI_API_KEY=your_gemini_api_key_here
   ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
   ```

4. **Run the application**:
   ```bash
   python main.py
   ```

5. **Open your browser** and navigate to `http://localhost:5000`

## 🔑 API Keys Setup

### Gemini API Key (Required)
1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Create a new API key
3. Add it to your `.env` file as `GEMINI_API_KEY`

### ElevenLabs API Key (Optional - for voice narration)
1. Sign up at [ElevenLabs](https://elevenlabs.io)
2. Go to [API Settings](https://elevenlabs.io/app/settings/api-keys)
3. Copy your API key
4. Add it to your `.env` file as `ELEVENLABS_API_KEY`

> **Note**: Without API keys, the app will still work but will show placeholder images and skip audio generation.

## 📖 How to Use

### Creating Your First Comic

1. **Start a New Comic**:
   - Enter a title for your comic
   - Choose an art style (realistic, cartoon, manga, etc.)
   - Add an optional story description

2. **Define Characters**:
   - Click "Add Character" to define your cast
   - Provide names, descriptions, and appearance details
   - Characters will be maintained consistently across panels

3. **Generate Panels**:
   - Write a scene description for each panel
   - Be specific about actions, emotions, and settings
   - Mention characters by name when they appear

4. **Edit Panels** (Optional):
   - Use natural language to modify panels
   - Examples: "make it nighttime", "add rain", "change expression to happy"

5. **Add Narration** (Optional):
   - Write narration text for any panel
   - AI will generate voice audio automatically (if ElevenLabs API key is provided)

6. **Export Your Comic**:
   - Click "Export PDF" to download your finished comic
   - The PDF includes all panels, descriptions, and narration text

### Tips for Better Results

- **Be Descriptive**: The more detailed your scene descriptions, the better the generated images
- **Character Consistency**: Always mention character names in scene descriptions
- **Style Consistency**: Stick to one art style throughout your comic
- **Logical Flow**: Create panels that tell a coherent story

## 🛠️ Technical Details

### Project Structure
