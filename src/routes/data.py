from fastapi import FastAPI,APIRouter, Depends,UploadFile,status, Request
from fastapi.responses import JSONResponse
import os
from helpers.config import get_settings,Settings
from controllers import DataController,ProjectController,ProcessController
import aiofiles
from models import ResponseSignal
import logging
from .schemes.data import ProcessingRequest
from models.ProjectModel import ProjectModel
from models.ChunkModel import ChunkModel
from models.db_schemas import DataChunk,Asset
from models.AssetModel import AssetModel
from models.enums import AssetTypeEnum
from datetime import datetime
from controllers import NLPController


logger = logging.getLogger("uvicorn.error")

data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["data"]
)

# For upload data and make it chunks
@data_router.get("/upload/{project_id}")
async def upload_data(request:Request,project_id:int ,file:UploadFile ,
                      app_settings: Settings = Depends(get_settings)):

    """
    First i Check if i have this project or not
    if yes:
        i go to the project folder
    if no:
        i create the project folder
    then i check if file that he uploaded is valid based on my credintials:
    1. file extension
    2. file size
    3. file type

    if file is valid:
        i save the file in the project folder
        i create a record in the database for the file
        i return the file id
    else:
        i return the error message
    """

    print("11")
    # Validata the file properties
    data_controller = DataController()

    # it will work like start engine of car
    # it will create a connection to the database
    # and it will return the connection
    project_model = await ProjectModel.create_instance(
        db_client=request.app.db_client,
    )

    # get project details
    # if project is not found it will create it
    project = await project_model.get_project_or_create_one(
        project_id=project_id,
    )

    # Validata the file properties based on our credintials
    # Such as : file extension , file size , file type
    is_valid,result_Signals = data_controller.validate_uploaded_file(file=file)

    if not is_valid:
        return JSONResponse(status_code=status.HTTP_409_CONFLICT,content={"Signals":result_Signals})
    
    # get project path
    project_dir_path = ProjectController().get_project_path(project_id=project_id)
    
    # generate unique file path
    # it will return the file path and file id
    # For make sure there is no duplicate file name
    file_path, file_id  = data_controller.generate_unique_filepath(
        orig_file_name=file.filename,
        project_id=project_id
    )

    # save file
    # it will save the file in the project folder
    # and it will return the file path
    try:
        async with aiofiles.open(file_path, "wb") as f:
            while chunk := await file.read(app_settings.FILE_DEFAULT_CHUNK_SIZE):
                await f.write(chunk)
    except Exception as e:
        logger.error(f"Error while uploading file {e}")
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,content={"Signals":ResponseSignal.FILE_NOT_SAVED.value})

    # After save file in project Folder
    # it will go to the database and create a record for the file
    # By using AssetModel class
    # create asset model
    # it will work like start engine of car
    # it will create a connection to the database
    # and it will return the connection
    asset_model = await AssetModel.create_instance(
        db_client=request.app.db_client,
    )

    # create asset resource
    # it will create a record for the file
    # and it will return the record
    asset_resource = Asset(
        asset_project_id=project.project_id,
        asset_type=AssetTypeEnum.FILE_.value,
        asset_name=file_id,
        asset_size=str(os.path.getsize(file_path)),
    )

    # then save it in the database
    asset_record = await asset_model.create_asset(asset=asset_resource)

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "Signals":ResponseSignal.FILE_UPLOADED_SUCCESSFULLY.value,
            "file_id": str(asset_record.asset_id),
            "file_name": asset_record.asset_name,
            }
        )


# For process the file content and get content
@data_router.get("/process/{project_id}")
async def process_endpoint(request:Request,project_id:int, proecess_request:ProcessingRequest):
    """
    This endpoint is used to process the file content and get content
    This endpoint does:

    1. Get project
    2. Get file(s)
    3. Chunk file content
    4. Store chunks in DB
    5. Return stats(no_chunks, no_files)
    
    Args:
        project_id (str): The ID of the project
        file_id (str): The ID of the file
        chunk_size (int): The size of the chunks
        overlap_size (int): The size of the overlap
        do_reset (bool): Whether to reset the process
    
    Returns:
        JSONResponse: The response object have :
            1- no_chunks
            2- no_files
    """


    # First get the project details
    # that i need to perform the process of RAG 
    # get the file id
    file_id = proecess_request.file_id
    # get the chunk size
    chunk_size = proecess_request.chunk_size
    # get the overlap size
    overlap_size = proecess_request.overlap_size
    # get the do_reset
    do_reset = proecess_request.do_reset

    # create project model
    # it will work like start engine of car
    # it will create a connection to the database
    # and it will return the connection
    project_model = await ProjectModel.create_instance(
        db_client=request.app.db_client
        )

    # get project details
    # if project is not found it will create it
    project = await project_model.get_project_or_create_one(project_id=project_id)

    nlp_controller =NLPController(
        vectordb_client=request.app.vectordb_client,
        generation_client=request.app.generation_client,
        embedding_client=request.app.embedding_client,
        template_parser=request.app.template_parser,
    )
    # create asset model
    # it will work like start engine of car
    # it will create a connection to the database
    # and it will return the connection
    asset_model = await AssetModel.create_instance(
        db_client=request.app.db_client
        )

    # create a dictionary for the file ids
    # it will store the file ids
    # and the file names
    project_files_ids={}

    # if file_id is provided and send by user
    # we need to process that file only
    if proecess_request.file_id:
        asset_record = await asset_model.get_asset_record(
            asset_project_id=project.project_id,
            asset_name=proecess_request.file_id
            )

        if asset_record is None:
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"Signals":ResponseSignal.FILE_ID_NOT_FOUND.value})
       
        project_files_ids = {
            asset_record.asset_project_id: asset_record.asset_name
        }
    
    # if file_id is not provided 
    # we need to get all files in the project
    # and process them
    else:
        # get the file project indexes
        project_files  = await asset_model.get_all_projects(
            asset_project_id=project.project_id,
            asset_type=AssetTypeEnum.FILE_.value
            )
        project_files_ids = {
            record.asset_id: record.asset_name
            for record in project_files
        }

        if len(project_files_ids)==0:
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"Signals":ResponseSignal.NO_FILE_FOUND_IN_PROJECT.value})


    # create process controller
    # His mission is controll 
    process_controller = ProcessController(project_id=project_id)

    # create chunk model
    # it will work like start engine of car
    # it will create a connection to the database
    # and it will return the connection
    chunk_model = await ChunkModel.create_instance(db_client=request.app.db_client)

    # delete old chunks if do_reset is True
    if do_reset == 1:
        # delete associated vectors collection
        collection_name = nlp_controller.create_collection_name(project_id=project.project_id)
        _ = await request.app.vectordb_client.delete_collection(collection_name=collection_name)

        # delete associated chunks
        _ = await chunk_model.delete_chunks_by_project_id(
            project_id=project.project_id
        )

    no_records=0
    no_files=0
    # process each file (one by one file) from files that in project_files_ids
    # by chunking the file content
    # and store the chunks in the database
    # get also count no_chunks, no_files
    for asset_id, file_id in project_files_ids.items():
        # get file content
        file_content = process_controller.get_file_content(file_id=file_id)

        if file_content is None:
            logger.error(f"Error while processing file {file_id}")
            continue
       
        file_chunks = process_controller.process_file_content(
            file_content=file_content,
            file_id=file_id,
            chunk_size=chunk_size,
            overlap_size=overlap_size
        )
        if file_chunks is None or len(file_chunks) == 0:
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"Signals":ResponseSignal.PROCESSING_FAILED.value})


        file_chunks_records = [
            DataChunk(
                chunk_text=chunk.page_content,
                chunk_metadata=chunk.metadata,
                chunk_order=chunk_index+1,
                chunk_project_id=project.project_id,
                chunk_asset_id=asset_id
            )
            for chunk_index, chunk in enumerate(file_chunks)
        ]
        
        no_records += await chunk_model.insert_many_chunks(chunks=file_chunks_records)
        no_files += 1


    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "Signals":ResponseSignal.PROCESSING_SUCCESSFULLY.value,
            "inserted_chunks":no_records,
            "processed_files":no_files,
            }
        )

