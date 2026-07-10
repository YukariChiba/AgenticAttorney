import re

from src.core.director.assets import AssetsManager
from src.types.director.frames import Frame

MAX_CONTENT_LENGTH = 100

_BGM_PATTERN = re.compile(r"\[#bgm(\d+)\]")
_BGS_PATTERN = re.compile(r"\[#bgs(\d+)\]")
_MISSING_HASH_BGM = re.compile(r"\[bgm\d+\]")
_MISSING_HASH_BGS = re.compile(r"\[bgs\d+\]")

_COLOR_OPEN = re.compile(r"\[#/[^\]]+\]")
_EFFECT_TAGS = re.compile(
    r"\[#(?:bgm\d+|bgs\d+|bgms|bgmfi|bgmfo|bgss|p\d+|w\d+|ts\d+|fs|fm|fl)\]"
)


class FrameValidator:
    def __init__(self, assets_manager: AssetsManager):
        self.assets = assets_manager
        self._valid_music_ids = {m.id for m in assets_manager.fetch_music()}
        self._valid_sound_ids = {s.id for s in assets_manager.fetch_sounds()}

    def _validate_content_tags(self, content: str, frame_id: int) -> str | None:
        open_tag_pattern = r"(\[#/[^\]]+\])"
        open_tags = re.findall(open_tag_pattern, content)

        close_tags_count = content.count("[/#]")

        if len(open_tags) != close_tags_count:
            if open_tags:
                return f"Frame {frame_id}: Found {len(open_tags)} opening tags ({[f'{tag}' for tag in open_tags]}) but {close_tags_count} closing tags ([/#]) in content"

        return None

    def _validate_self_closing_tags(self, content: str, frame_id: int) -> str | None:
        color_opens = len(_COLOR_OPEN.findall(content))
        close_count = content.count("[/#]")

        if close_count > color_opens:
            effect_count = len(_EFFECT_TAGS.findall(content))
            return (
                f"Frame {frame_id}: Found {close_count} closing tags [/#] but only "
                f"{color_opens} color opening tags ([#/r], [#/b], [#/g], [#/y]). "
                f"The extra {close_count - color_opens} [/#] tag(s) are likely attached "
                f"to self-closing effect tags ({effect_count} found: BGM/BGS/pause/flash). "
                f"Effect tags do NOT need [/#]. Only color tags do."
            )

        return None

    def _validate_tag_hashes(self, content: str, frame_id: int) -> str | None:
        if _MISSING_HASH_BGM.search(content):
            match = _MISSING_HASH_BGM.search(content)
            return f"Frame {frame_id}: BGM tag missing '#': '{match.group(0)}' should be '[#bgm...]'"

        if _MISSING_HASH_BGS.search(content):
            match = _MISSING_HASH_BGS.search(content)
            return f"Frame {frame_id}: BGS tag missing '#': '{match.group(0)}' should be '[#bgs...]'"

        return None

    def _validate_bgm_bgs_ids(self, content: str, frame_id: int) -> str | None:
        bgm_ids = _BGM_PATTERN.findall(content)
        for bgm_id in bgm_ids:
            if int(bgm_id) not in self._valid_music_ids:
                return f"Frame {frame_id}: BGM ID {bgm_id} not found in available music list"

        bgs_ids = _BGS_PATTERN.findall(content)
        for bgs_id in bgs_ids:
            if int(bgs_id) not in self._valid_sound_ids:
                return f"Frame {frame_id}: Sound effect ID {bgs_id} not found in available sound list"

        return None

    def validate_frame(self, frame: Frame, frame_id: int) -> str | None:
        if len(frame.content) > MAX_CONTENT_LENGTH:
            return f"Frame {frame_id}: Content too long ({len(frame.content)} chars, max {MAX_CONTENT_LENGTH})"

        content_error = self._validate_content_tags(frame.content, frame_id)
        if content_error:
            return content_error

        stray_error = self._validate_self_closing_tags(frame.content, frame_id)
        if stray_error:
            return stray_error

        hash_error = self._validate_tag_hashes(frame.content, frame_id)
        if hash_error:
            return hash_error

        bgm_error = self._validate_bgm_bgs_ids(frame.content, frame_id)
        if bgm_error:
            return bgm_error

        char_data = self.assets.get_character_info(frame.character)
        if not char_data:
            return (
                f"Frame {frame_id}: Character info not found for ID: {frame.character}"
            )

        if frame.pose not in char_data.poses.values():
            if char_data.poses:
                return f"Frame {frame_id}: Pose not found for character {char_data.name}({char_data.id}): {frame.pose}. Available poses: {', '.join([f'{pose}({char_data.poses[pose]})' for pose in char_data.poses.keys()])}"
            else:
                return f"Frame {frame_id}: Pose not found for character {char_data.name}({char_data.id}): {frame.pose} and no default pose available"

        if frame.bubble and frame.bubble not in char_data.speechBubbles.values():
            return f"Frame {frame_id}: Bubble not found for character {char_data.name}({char_data.id}): {frame.bubble}. Available bubbles: {', '.join([f'{bubble}({char_data.speechBubbles[bubble]})' for bubble in char_data.speechBubbles.keys()])}"

        return None
