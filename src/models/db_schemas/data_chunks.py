from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from bson.objectid import ObjectId
import pymongo

class DataChunk(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: Optional[ObjectId] = Field(None,alias="_id")
    project_id: str = Field(..., min_length=1)
    chunk_text: str = Field(..., min_length=1)
    chunk_metadata: dict
    chunk_order: int = Field(..., gt=0)
    chunk_project_id: ObjectId
    chunk_asset_id: ObjectId


    # Build for make the read from DB more Efficient and Fast
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
                "name": "chunk_project_id_order_idx",
                "keys": [("chunk_project_id", pymongo.ASCENDING), ("chunk_order", pymongo.ASCENDING)],
                "unique": True
            },
            {
                "name": "chunk_project_id_idx",
                "keys": [("chunk_project_id", pymongo.ASCENDING)],
                "unique": False
            }
        ]


class RetrieveDocument(BaseModel):
    """
    Retrieve Document his mission is be as Parse for output 

    Args:
        text (str): The text of the document.
        score (float): The score of the document.
    
    """
    text: str
    score: float
    # metadata: dict

