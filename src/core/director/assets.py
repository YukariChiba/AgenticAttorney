import json
from typing import Any

import requests_cache

from src.constants import DIRECTOR_DATA_DIR
from src.types.director.presets import Character, Music, Sound

API_URL = "https://objection.lol/api"


def _fetch_json(
    session: requests_cache.CachedSession, endpoint: str
) -> list[dict[str, Any]]:
    url = f"{API_URL}/assets/{endpoint}/getPreset"
    response = session.get(url=url)
    return response.json()


class AssetsManager:
    def __init__(self, cache_duration: int = 86400):
        self.session = requests_cache.CachedSession(
            "cache/objection_api", expire_after=cache_duration
        )
        self._characters: list[Character] | None = None
        self._music: list[Music] | None = None
        self._sounds: list[Sound] | None = None

    def fetch_characters(self) -> list[Character]:
        if self._characters is not None:
            return self._characters

        characters_data = _fetch_json(self.session, "character")

        self._characters = []
        for char in characters_data:
            self._characters.append(
                Character(
                    id=char["id"],
                    name=char["name"],
                    side=char.get("side"),
                    backgroundId=char.get("backgroundId"),
                    poses={pose["name"]: pose["id"] for pose in char["poses"]},
                    speechBubbles={
                        bubble["name"]: bubble["id"]
                        for bubble in char.get("speechBubbles", [])
                    },
                )
            )

        return self._characters

    def fetch_music(self) -> list[Music]:
        if self._music is not None:
            return self._music

        music_data = _fetch_json(self.session, "music")

        self._music = []
        for music in music_data:
            self._music.append(Music(id=music["id"], name=music["name"]))

        return self._music

    def fetch_sounds(self) -> list[Sound]:
        if self._sounds is not None:
            return self._sounds

        sounds_data = _fetch_json(self.session, "sound")

        self._sounds = []
        for sound in sounds_data:
            self._sounds.append(Sound(id=sound["id"], name=sound["name"]))

        return self._sounds

    def get_character_info(self, character_id: int) -> Character | None:
        if self._characters is None:
            self.fetch_characters()

        chars = self._characters
        if chars is None:
            return None
        return next((x for x in chars if x.id == character_id), None)

    def get_pose_id(self, character_id: int, pose_name: str) -> int | None:
        char_info = self.get_character_info(character_id)
        if not char_info:
            return None
        return char_info.poses.get(pose_name)

    def get_bubble_id(self, character_id: int, bubble_name: str) -> int | None:
        char_info = self.get_character_info(character_id)
        if not char_info:
            return None
        return char_info.speechBubbles.get(bubble_name)

    def get_background_id(self, side: str) -> int:
        background_file = DIRECTOR_DATA_DIR / "background.json"
        with open(background_file, encoding="utf-8") as f:
            background_mapping = json.load(f)
        result = background_mapping.get(side, 177)
        return result if result is not None else 177
