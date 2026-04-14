import re
from pathlib import Path
from typing import List

from services.sound_effect.config import SoundEffectConfig


class TextSegment:
    """Represents a segment of text, either plain text or a sound effect."""

    def __init__(self, text: str = None, sound_effect_id: str = None):
        self.text = text
        self.sound_effect_id = sound_effect_id
        self.is_sound_effect = sound_effect_id is not None

    def __repr__(self):
        if self.is_sound_effect:
            return f"TextSegment(sound_effect_id={self.sound_effect_id})"
        else:
            return f"TextSegment(text={repr(self.text)})"


class SoundEffectService:
    def __init__(self, config: SoundEffectConfig):
        self._sound_effect_dir = Path(config.sound_effect_dir)
        self._sound_effect_dir.mkdir(parents=True, exist_ok=True)
        # Cache the valid sound effect IDs
        self._valid_sound_effect_ids_cache = None

    def get_valid_sound_effect_ids(self, ) -> List[str]:
        """
        Get valid sound effect IDs by scanning the sound effect directory.
        :return: List of valid sound effect IDs (file names without extension)
        """
        sounds_dir = self._sound_effect_dir
        valid_ids = []

        # Supported audio file extensions
        audio_extensions = {'.mp3', '.wav', '.ogg', '.m4a', '.flac'}

        if sounds_dir.exists():
            for file_path in sounds_dir.iterdir():
                if file_path.is_file():
                    # Get file name without extension
                    stem = file_path.stem
                    # Check if it's an audio file
                    if file_path.suffix.lower() in audio_extensions:
                        valid_ids.append(stem)

        # Sort for consistency
        valid_ids.sort()
        return valid_ids

    def get_cached_valid_sound_effect_ids(self, ) -> List[str]:
        """
        Get cached valid sound effect IDs, refreshing if cache is empty.
        :return: List of valid sound effect IDs
        """
        if self._valid_sound_effect_ids_cache is None:
            self._valid_sound_effect_ids_cache = self.get_valid_sound_effect_ids()
        return self._valid_sound_effect_ids_cache

    def refresh_sound_effect_ids_cache(self, ):
        """Refresh the cache of valid sound effect IDs."""
        self._valid_sound_effect_ids_cache = None

    def parse_sound_effect_markers(self, text: str) -> List[TextSegment]:
        """
        Parse text and extract sound effect JSON markers like {"sound_effect_id": "xxx"}.
        Returns a list of TextSegment objects, alternating between text and sound effect markers.

        Example:
            Input: 'Hello {"sound_effect_id": "bruh"} world'
            Output: [
                TextSegment(text='Hello '),
                TextSegment(sound_effect_id='bruh'),
                TextSegment(text=' world')
            ]
        """
        segments = []

        # Pattern to match JSON objects like {"sound_effect_id": "xxx"}
        pattern = r'\{\s*"sound_effect_id"\s*:\s*"([^"]+)"\s*\}'

        # Get valid sound effect IDs
        valid_ids = self.get_cached_valid_sound_effect_ids()

        last_end = 0
        for match in re.finditer(pattern, text):
            # Add text before the match
            if match.start() > last_end:
                segment_text = text[last_end:match.start()]
                if segment_text:
                    segments.append(TextSegment(text=segment_text))

            # Add sound effect marker
            sound_effect_id = match.group(1)
            # Validate sound effect ID
            if sound_effect_id in valid_ids:
                segments.append(TextSegment(sound_effect_id=sound_effect_id))
            else:
                # If invalid, keep it as text
                segments.append(TextSegment(text=match.group(0)))

            last_end = match.end()

        # Add remaining text
        if last_end < len(text):
            segment_text = text[last_end:]
            if segment_text:
                segments.append(TextSegment(text=segment_text))

        # If no markers found, return the whole text as a single segment
        if not segments:
            segments.append(TextSegment(text=text))

        return segments

    def get_sound_effect_path(self, sound_effect_id: str, sounds_dir: Path = None) -> Path | None:
        """
        Get the path to a sound effect file.
        :param sound_effect_id: The sound effect ID (e.g., "bruh")
        :param sounds_dir: The base directory for sounds (default: resources/static/sounds/effect)
        :return: Path to the sound file, or None if not found
        """
        if sounds_dir is None:
            sounds_dir = self._sound_effect_dir

        # Supported audio file extensions (in order of preference)
        audio_extensions = ['.mp3', '.wav', '.ogg', '.m4a', '.flac']

        for ext in audio_extensions:
            sound_file = sounds_dir / f"{sound_effect_id}{ext}"
            if sound_file.exists():
                return sound_file

        return None
