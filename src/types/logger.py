from typing import TypedDict


class LogEntry(TypedDict):
    name: str
    objlol_id: int
    role: str
    content: str
