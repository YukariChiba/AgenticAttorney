import chevron

from src.core.director.assets import AssetsManager
from src.core.director.format import (
    format_characters_info,
    format_music_list,
    format_sound_list,
)
from src.types.director.presets import Character, Music, Sound
from src.types.logfile import LogEntry


class PromptBuilder:
    def __init__(
        self,
        active_characters: list[Character],
        music: list[Music],
        sounds: list[Sound],
        tags: dict,
    ):
        self.active_characters = active_characters
        self.music = music
        self.sounds = sounds
        self.tags = tags

    def build_system_prompt(self, system_template: str) -> str:
        characters_info = (
            format_characters_info(self.active_characters)
            if self.active_characters
            else "No active characters available"
        )
        music_list = format_music_list(self.music)
        sound_list = format_sound_list(self.sounds)
        tags_info = "\n".join([f"{tag}: {desc}" for tag, desc in self.tags.items()])

        return chevron.render(
            system_template,
            {
                "characters_info": characters_info,
                "music_list": music_list,
                "sound_list": sound_list,
                "tags": tags_info,
            },
        )

    def build_user_prompt(
        self,
        user_template: str,
        log_entry: LogEntry,
        next_log_entry: LogEntry | None,
        previous_frames: list,
        assets_manager: AssetsManager,
    ) -> str:
        speaker_cn = log_entry.name
        char_id = log_entry.objlol_id
        content = log_entry.content

        character = next((c for c in self.active_characters if c.id == char_id), None)
        char_info = (
            character if character else assets_manager.get_character_info(char_id)
        )
        speaker_en = char_info.name if char_info else "unknown"
        side = char_info.side if char_info else "unknown"

        recent_frames_str = self._format_recent_frames(previous_frames)

        next_log_str = self._format_next_log(next_log_entry)

        return chevron.render(
            user_template,
            {
                "speaker_cn": speaker_cn,
                "speaker_en": speaker_en,
                "side": side,
                "content": content,
                "recent_frames": recent_frames_str,
                "next_log": next_log_str,
            },
        )

    def _format_recent_frames(self, previous_frames: list) -> str:
        if not previous_frames:
            return ""

        frames_text = []
        for i, frame in enumerate(previous_frames):
            frames_text.append(
                f"  {i + 1}. 角色 ID: {frame.character}\n     {frame.content}"
            )

        return "\n".join(frames_text)

    def _format_next_log(self, next_log_entry: LogEntry | None) -> str:
        if next_log_entry is None:
            return "（无后续台词，这是最后一句）"

        speaker_cn = next_log_entry.name
        char_id = next_log_entry.objlol_id
        content = next_log_entry.content

        character = next((c for c in self.active_characters if c.id == char_id), None)
        speaker_en = character.name if character else "unknown"

        return f'{speaker_cn} ({speaker_en}):\n  "{content}"'
