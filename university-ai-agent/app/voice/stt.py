import io
import wave
import pyaudio
from faster_whisper import WhisperModel
from app.core.logger import logger

class SpeechToText:
    """Convert speech to text using faster-whisper (Python 3.13 compatible)"""

    def __init__(self):
        # Using tiny model for speed; change to "base" or "small" for better accuracy
        self.model = WhisperModel("tiny", device="cpu", compute_type="int8")
        self.audio = pyaudio.PyAudio()
        self.sample_rate = 16000
        self.chunk = 1024
        self.channels = 1
        self.record_seconds = 5

    def _record_audio(self) -> bytes:
        """Record audio from microphone"""
        stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=self.channels,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=self.chunk
        )
        logger.info("Listening...")
        frames = []
        for _ in range(0, int(self.sample_rate / self.chunk * self.record_seconds)):
            data = stream.read(self.chunk, exception_on_overflow=False)
            frames.append(data)
        stream.stop_stream()
        stream.close()
        return b"".join(frames)

    def _bytes_to_wav(self, audio_bytes: bytes) -> io.BytesIO:
        """Convert raw bytes to WAV format in memory"""
        buf = io.BytesIO()
        with wave.open(buf, "wb") as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
            wf.setframerate(self.sample_rate)
            wf.writeframes(audio_bytes)
        buf.seek(0)
        return buf

    def listen(self) -> str:
        """Listen to microphone and convert to text"""
        try:
            audio_bytes = self._record_audio()
            wav_buf = self._bytes_to_wav(audio_bytes)
            segments, _ = self.model.transcribe(wav_buf, language="en")
            text = " ".join(seg.text for seg in segments).strip()
            logger.info(f"Recognized: {text}")
            return text
        except Exception as e:
            logger.error(f"STT error: {e}")
            return ""

    def from_audio_file(self, file_path: str) -> str:
        """Convert audio file to text"""
        try:
            segments, _ = self.model.transcribe(file_path, language="en")
            text = " ".join(seg.text for seg in segments).strip()
            logger.info(f"Transcribed from file: {text}")
            return text
        except Exception as e:
            logger.error(f"File transcription error: {e}")
            return ""

stt = SpeechToText()
