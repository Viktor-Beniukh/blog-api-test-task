import re


def slugify(s):
    pattern = r"[^\w+]"
    return re.sub(pattern, "-", s)


def format_tag_name(name: str) -> str:
    if not name.startswith("#"):
        return f"#{name.lower()}"
    return name.lower()
