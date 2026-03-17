import frontmatter


def load_md_raw(file: str):
    with open(f"prompts/{file}.md", encoding="utf-8") as f:
        return f.read()


def load_md(file: str):
    return frontmatter.loads(load_md_raw(file))


def load_frontmatter(file: str) -> dict[str, object]:
    return load_md(file).metadata


def load_content(file: str) -> str:
    return load_md(file).content
