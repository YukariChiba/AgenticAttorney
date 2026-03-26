from src.types.director.presets import Character, Music, Sound


def format_characters_info(characters: list[Character]) -> str:
    if not characters:
        return "No characters available"

    lines = []
    for char in characters:
        poses_str = ", ".join([f'"{p}"({pid})' for p, pid in list(char.poses.items())])

        bubbles_str = ", ".join(
            [f'"{b}"({bid})' for b, bid in list(char.speechBubbles.items())]
        )

        side_str = char.side if char.side else "unknown"
        lines.append(
            f"- {char.name} (ID:{char.id}) [{side_str}]\n  可用姿势: {poses_str}\n  可用气泡: {bubbles_str}"
        )

    return "\n".join(lines)


def format_music_list(music: list[Music]) -> str:
    if not music:
        return "No music available"

    lines = []
    for track in music:
        lines.append(f"[{track.id}] {track.name}")
    return "\n".join(lines)


def format_sound_list(sounds: list[Sound]) -> str:
    if not sounds:
        return "No sounds available"

    lines = []
    for sound in sounds:
        lines.append(f"[{sound.id}] {sound.name}")
    return "\n".join(lines)
