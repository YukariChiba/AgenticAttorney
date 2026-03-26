from pydantic import BaseModel


class LogEntry(BaseModel):
    name: str
    objlol_id: int
    role: str
    content: str

    class Config:
        populate_by_name = True
        extra = "allow"
