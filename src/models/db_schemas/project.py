from pydantic import BaseModel,Field,validator
from typing import Optional
from bson.objectid import ObjectId
from pydantic import ConfigDict
import pymongo


class Project(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )
    
    id: Optional[ObjectId] = Field(None,alias="_id")
    project_id:str = Field(...,min_length=1)
    
    
    @validator("project_id")
    def project_id_must_be_unique(cls, value):
        if not value.isalnum():
            raise ValueError("project_id must be alphanumeric")
        return value

    @classmethod
    def get_indexes(cls):
        """
        Returns indexes in a consistent format:
        [
            {
                "name": "index_name",
                "keys": [("field_name", pymongo.ASCENDING), ...],
                "unique": True/False
            },
            ...
        ]
        """
        return [
            {
                "name": "project_id_unique_idx",
                "keys": [("project_id", pymongo.ASCENDING)],
                "unique": True
            },
            {
                "name": "name_idx",
                "keys": [("name", pymongo.ASCENDING)],
                "unique": False
            }
        ]
