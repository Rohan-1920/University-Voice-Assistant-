import pyaudio
import requests
from app.core.config import config
from app.core.logger import logger


class TextToSpeech:
    """Humanized Text to Speech using ElevenLabs REST API directly"""

    def __init__(self):
        self.api_key = config.ELEVENLABS_API_KEY
        self.voice_id = "NDTYOmYEjbDIVCKB35i3"
        self.audio = pyaudio.PyAudio()

    def speak(self, text: str):
        """Convert text to speech via ElevenLabs API and play it"""
        try:
            logger.info(f"Speaking: {text}")

            response = requests.post(
                f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}",
                headers={
                    "xi-api-key": self.api_key,
                    "Content-Type": "application/json",
                    "Accept": "audio/mpeg"
                },
                json={
                    "text": text,
                    "model_id": "eleven_multilingual_v2",
                    "voice_settings": {
                        "stability": 0.5,
                        "similarity_boost": 0.75,
                        "style": 0.3,
                        "use_speaker_boost": True
                    }
                },
                timeout=30
            )

            if response.status_code == 200:
                self._play_mp3(response.content)
            else:
                logger.error(f"ElevenLabs error: {response.status_code}")
                self._fallback_speak(text)

        except Exception as e:
            logger.error(f"TTS error: {e}")
            self._fallback_speak(text)

    def _play_mp3(self, audio_bytes: bytes):
        """Play MP3 audio bytes"""
        try:
            import io
            from pydub import AudioSegment
            from pydub.playback import play

            audio = AudioSegment.from_mp3(io.BytesIO(audio_bytes))
            play(audio)
        except Exception as e:
            logger.error(f"Audio playback error: {e}")
            self._fallback_speak("")

    def _fallback_speak(self, text: str):
        """Fallback to pyttsx3"""
        try:
            import pyttsx3
            engine = pyttsx3.init()
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            logger.error(f"Fallback TTS error: {e}")


tts = TextToSpeech()
