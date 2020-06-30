from datetime import datetime
from io import BytesIO
from typing import List, Optional, Set

from pydantic import BaseModel, validator, Field
from PIL import Image


class File(BaseModel):
    source_id: str
    name: str
    date_modified: datetime = Field(..., alias="modifiedTime")
    mime_type: str = Field(..., alias="mimeType")
    source: str
    content: Optional[BytesIO]

    class Config:
        arbitrary_types_allowed = True


class Files(BaseModel):

    __root__: List[File]

    def __getitem__(self, item):
        return self.__root__[item]


JSON_CONFIG = {"by_alias": True, "exclude": {"__root__": {"__all__": {"content"}}}}



class Note(File):
    tags: List[str] = []
    folder: str = ''
    title: str = ''
    text: str = ''


