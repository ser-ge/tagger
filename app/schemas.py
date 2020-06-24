from datetime import datetime
from io import BytesIO
from typing import List, Optional, Set

from pydantic import BaseModel, validator, Field


class File(BaseModel):
    id: str
    name: str
    date_modified: datetime = Field(..., alias="modifiedTime")
    mime_type: str = Field(..., alias="mimeType")
    content: Optional[BytesIO]

    class Config:
        arbitrary_types_allowed = True


class Files(BaseModel):

    __root__: List[File]

    def __getitem__(self, item):
        return self.__root__[item]


JSON_CONFIG = {"by_alias": True, "exclude": {"__root__": {"__all__": {"content"}}}}
