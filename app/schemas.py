from datetime import datetime
from io import BytesIO
from typing import List, Optional, Set

from pydantic import BaseModel, validator, Field


class CustomBase(BaseModel):
    class Config:
        include: Set[str] = set()
        exclude: Set[str] = set()

    def json(self, **kwargs):
        '''
        overides json method to allow setting exclude / include in Config
        instead of calling  model.json(exclude={'key':...}) on every instance
        '''
        include = kwargs.pop('include', set())
        include = include.union(getattr(self.Config, "include", set()))
        if len(include) == 0:
            include = None

        exclude = kwargs.pop('exclude', set())
        exclude = exclude.union(getattr(self.Config, "exclude", set()))
        if len(exclude) == 0:
            exclude = None

        return super().json(include=include, exclude=exclude, **kwargs)


class File(CustomBase):
    id: str
    name: str
    date_modified: datetime = Field(..., alias='modifiedTime')
    mime_type: str = Field(..., alias='mimeType')
    content: Optional[BytesIO]

    class Config:
        arbitrary_types_allowed = True
        exclude = {'content'}


class Files(CustomBase):

    __root__: List[File]

    def __getitem__(self, item):
        return self.__root__[item]




