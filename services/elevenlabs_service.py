import os
import logging
import requests
from datetime import datetime

def generate_narration_audio(text, panel_id):
    """
    Generate audio narration using ElevenLabs TTS API
    
    Args:
        text (str): Text to convert to speech
        panel_id (int): Panel ID for file naming
    
    Returns:
        str: Path to the generated audio file, or None if failed
    """
    try:
        api_key = os.environ.get("ELEVENLABS_API_KEY")
        
        if not api_key:
            logging.warning("No ELEVENLABS_API_KEY found, skipping audio generation")
            return None
        
        # ElevenLabs API configuration
        voice_id = "21m00Tcm4TlvDq8ikWAM"  # Default voice (Rachel)
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": api_key
        }
        
        data = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.5,
                "style": 0.0,
                "use_speaker_boost": True
            }
        }
        
        logging.info(f"Generating audio for panel {panel_id}: {text[:50]}...")
        
        # Make request to ElevenLabs
        response = requests.post(url, json=data, headers=headers, timeout=30)
        
        if response.status_code == 200:
            # Ensure audio directory exists
            os.makedirs("static/audio", exist_ok=True)
            
            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            audio_path = f"static/audio/narration_{panel_id}_{timestamp}.mp3"
            
            # Save audio file
            with open(audio_path, 'wb') as f:
                f.write(response.content)
            
            logging.info(f"Audio saved as {audio_path}")
            return audio_path
        else:
            logging.error(f"ElevenLabs API error: {response.status_code} - {response.text}")
            return None
            
    except requests.exceptions.Timeout:
        logging.error("ElevenLabs API timeout")
        return None
    except requests.exceptions.RequestException as e:
        logging.error(f"ElevenLabs API request error: {e}")
        return None
    except Exception as e:
        logging.error(f"Error generating audio: {e}")
        return None

def get_available_voices():
    """
    Get list of available voices from ElevenLabs
    
    Returns:
        list: List of voice dictionaries, or empty list if failed
    """
    try:
        api_key = os.environ.get("ELEVENLABS_API_KEY")
        
        if not api_key:
            return []
        
        url = "https://api.elevenlabs.io/v1/voices"
        headers = {"xi-api-key": api_key}
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            voices_data = response.json()
            return voices_data.get("voices", [])
        else:
            logging.error(f"Error fetching voices: {response.status_code}")
            return []
            
    except Exception as e:
        logging.error(f"Error getting available voices: {e}")
        return []

def generate_audio_with_voice(text, voice_id, panel_id):
    """
    Generate audio with a specific voice
    
    Args:
        text (str): Text to convert to speech
        voice_id (str): ElevenLabs voice ID
        panel_id (int): Panel ID for file naming
    
    Returns:
        str: Path to the generated audio file, or None if failed
    """
    try:
        api_key = os.environ.get("ELEVENLABS_API_KEY")
        
        if not api_key:
            return None
        
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": api_key
        }
        
        data = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.5
            }
        }
        
        response = requests.post(url, json=data, headers=headers, timeout=30)
        
        if response.status_code == 200:
            os.makedirs("static/audio", exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            audio_path = f"static/audio/narration_{panel_id}_{timestamp}.mp3"
            
            with open(audio_path, 'wb') as f:
                f.write(response.content)
            
            return audio_path
        else:
            logging.error(f"ElevenLabs API error: {response.status_code}")
            return None
            
    except Exception as e:
        logging.error(f"Error generating audio with voice: {e}")
        return None
