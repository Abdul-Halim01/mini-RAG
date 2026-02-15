from .BaseDataModel import BaseDataModel
from .db_schemas import Project
from .enums.DataBaseEnum import DataBaseEnum
import pymongo


class ProjectModel(BaseDataModel):
    def __init__(self,db_client:object):
        super().__init__(db_client=db_client)
        self.collection = self.db_client[DataBaseEnum.COLLECTION_PROJECT_NAME.value]

    @classmethod
    async def create_instance(cls,db_client:object):
        instance = cls(db_client)
        await instance.init_collection()
        return instance
        
    async def init_collection(self):
        all_collection = await self.db_client.list_collection_names()
        if DataBaseEnum.COLLECTION_PROJECT_NAME.value not in all_collection:
            self.collection = self.db_client[DataBaseEnum.COLLECTION_PROJECT_NAME.value]
            indexes = Project.get_indexes()
            for index in indexes:
                # keys are already tuples: [("field", direction)]
                await self.collection.create_index(
                    index["keys"],
                    name=index["name"],
                    unique=index["unique"]
                )

    async def create_project(self,project:Project):
        result = await self.collection.insert_one(project.dict(by_alias=True,exclude_none=True))
        project = result.inserted_id
        return project

    # get project or create one
    async def get_project_or_create_one(self, project_id: str):

        # get project from DB
        record = await self.collection.find_one({
            "project_id": project_id
        })

        # if project is not found create new project
        if record is None:
            # create new project
            project = Project(project_id=project_id)
            project = await self.create_project(project=project)

            return project
        
        print("Record",record)
        temp_project= Project(**record)
        print("###")
        print("temp_project",temp_project)
        print("###")
        return temp_project


    # get all projects
    async def get_all_projects(self, page:int =1, page_size: int=10 ):
        # Calculate total count of documents
        total_documents  = await self.collection.count_documents({})

        # Calculate the number of pages
        total_pages = (total_documents + page_size - 1) // page_size

        # Calculate the skip value
        skip = (page - 1) * page_size

        # get cursor from DB to Collect Documents
        cursor = await self.collection.find({}).skip(skip).limit(page_size)
        projects = []
        async for document in cursor:
            projects.append(
                Project(**document)
            )

        return projects,total_pages
        