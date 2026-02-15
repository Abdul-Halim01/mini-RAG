from .BaseDataModel import BaseDataModel
from .db_schemas import DataChunk
from .enums.DataBaseEnum import DataBaseEnum
from pymongo import InsertOne
from bson.objectid import ObjectId
import pymongo
from pymongo import UpdateOne


class ChunkModel(BaseDataModel):
    def __init__(self,db_client):
        super().__init__(db_client=db_client)
        self.collection = self.db_client[DataBaseEnum.COLLECTION_CHUNK_NAME.value]

    @classmethod
    async def create_instance(cls,db_client:object):
        instance = cls(db_client)
        await instance.init_collection()
        return instance
        
    async def init_collection(self):
        all_collection = await self.db_client.list_collection_names()
        if DataBaseEnum.COLLECTION_CHUNK_NAME.value not in all_collection:
            self.collection = self.db_client[DataBaseEnum.COLLECTION_CHUNK_NAME.value]
            indexes = DataChunk.get_indexes()
            for index in indexes:
                # keys are already tuples: [("field", direction)]
                await self.collection.create_index(
                    index["keys"],
                    name=index["name"],
                    unique=index["unique"]
                )


    async def create_chunk(self,chunk:DataChunk):
        result = await self.collection.insert_one(chunk.dict(by_alias=True,exclude_none=True))
        chunk._id = result.inserted_id
        return chunk

    async def get_chunk(self, chunk_id: str):
        record = await self.collection.find_one({
            "_id": ObjectId(chunk_id)
        })
        if record is None:
            return None

        return DataChunk(**record)


    async def insert_many_chunks(self, chunks: list[DataChunk], batch_size: int = 100):
        """
        Inserts multiple chunks in batches.
        Uses upsert to avoid duplicate key errors on (chunk_project_id, chunk_order)
        """
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]

            operations = [
                UpdateOne(
                    {"chunk_project_id": chunk.chunk_project_id, "chunk_order": chunk.chunk_order},
                    {"$set": chunk.dict(by_alias=True, exclude_none=True)},
                    upsert=True
                )
                for chunk in batch
            ]

            if operations:
                await self.collection.bulk_write(operations)

        return len(chunks)


    async def delete_chunks_by_project_id(self, project_id: ObjectId):
        result = await self.collection.delete_many({
            "chunk_project_id": project_id
        })
        return result.deleted_count