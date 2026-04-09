import pyttsx3
from app.core.config import config
from app.core.logger import logger

class TextToSpeech:
    """Convert text to speech"""

    def __init__(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', config.TTS_RATE)
        self.engine.setProperty('volume', config.TTS_VOLUME)

    def speak(self, text: str):
        """Speak the given text"""
        try:
            logger.info(f"Speaking: {text}")
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            logger.error(f"TTS error: {e}")

    def save_to_file(self, text: str, file_path: str):
        """Save speech to audio file"""
        try:
            self.engine.save_to_file(text, file_path)
            self.engine.runAndWait()
            logger.info(f"Saved audio to: {file_path}")
        except Exception as e:
            logger.error(f"TTS save error: {e}")

tts = TextToSpeech()
