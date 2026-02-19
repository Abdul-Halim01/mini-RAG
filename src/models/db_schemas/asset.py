from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from bson.objectid import ObjectId
import pymongo
from datetime import datetime

class Asset(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: Optional[ObjectId] = Field(None,alias="_id")
    asset_project_id: ObjectId 
    asset_type: str =Field(..., min_length=1)
    asset_name: str = Field(..., min_length=1)
    asset_size: int = Field(gt=0,default=None)
    asset_pushed_at: datetime = Field(default=datetime.now())
    asset_config: dict = Field(default=None)

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
                "name": "asset_project_id_unique_idx",
                "keys": [("asset_project_id", pymongo.ASCENDING)],
                "unique": False
            },
            {
                "name": "asset_name_project_id_unique_idx",
                "keys": [
                    ("asset_name", pymongo.ASCENDING),
                    ("asset_project_id", pymongo.ASCENDING)
                    ],
                "unique": True
            }
        ]
