import re

from src.core.director.assets import AssetsManager
from src.types.director.frames import Frame


class FrameValidator:
    def __init__(self, assets_manager: AssetsManager):
        self.assets = assets_manager

    def _validate_content_tags(self, content: str, frame_id: int) -> str | None:
        open_tag_pattern = r"(\[#/[^\]]+\])"
        open_tags = re.findall(open_tag_pattern, content)

        close_tags_count = content.count("[/#]")

        if len(open_tags) != close_tags_count:
            if open_tags:
                return f"Frame {frame_id}: Found {len(open_tags)} opening tags ({[f'{tag}' for tag in open_tags]}) but {close_tags_count} closing tags ([/#]) in content"

        return None

    def validate_frame(self, frame: Frame, frame_id: int) -> str | None:
        if len(frame.content) > 120:
            return f"Frame {frame_id}: Content too long"

        content_error = self._validate_content_tags(frame.content, frame_id)
        if content_error:
            return content_error

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
