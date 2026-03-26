import chevron
import frontmatter

from src.constants import PROMPTS_DIR
from src.types.config import AppConfig


class TemplateEngine:
    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self.prompts_dir = PROMPTS_DIR

    def _load_raw_content(self, filepath: str) -> str:
        full_path = self.prompts_dir / f"{filepath}.md"
        if not full_path.exists():
            raise FileNotFoundError(f"Prompt file not found: {full_path}")
        with open(full_path, encoding="utf-8") as f:
            return f.read()

    def _load_raw_frontmatter(self, filepath: str) -> dict[str, object]:
        content = self._load_raw_content(filepath)
        post = frontmatter.loads(content)
        return post.metadata

    def load_and_render(self, filepath: str, data: dict[str, str | int] | None = None):
        content = self._load_raw_content(filepath)
        if data:
            content = chevron.render(content, data)
        return frontmatter.loads(content)
