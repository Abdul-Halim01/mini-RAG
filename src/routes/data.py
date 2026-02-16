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


logger = logging.getLogger("uvicorn.error")

data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["data"]
)

# For upload data and make it chunks
@data_router.get("/upload/{project_id}")
async def upload_data(request:Request,project_id:str ,file:UploadFile ,
                      app_settings: Settings = Depends(get_settings)):

    print("11")
    # Validata the file properties
    data_controller = DataController()
    project_model = await ProjectModel.create_instance(
        db_client=request.app.db_client,
    )

    # get project details
    project = await project_model.get_project_or_create_one(
        project_id=project_id,
    )

    # Validata the file properties
    is_valid,result_Signals = data_controller.validate_uploaded_file(file=file)

    if not is_valid:
        return JSONResponse(status_code=status.HTTP_409_CONFLICT,content={"Signals":result_Signals})
    
    # get project path
    project_dir_path = ProjectController().get_project_path(project_id=project_id)
    
    # generate unique file path
    file_path, file_id  = data_controller.generate_unique_filepath(
        orig_file_name=file.filename,
        project_id=project_id
    )

    # save file
    try:
        async with aiofiles.open(file_path, "wb") as f:
            while chunk := await file.read(app_settings.FILE_DEFAULT_CHUNK_SIZE):
                await f.write(chunk)
    except Exception as e:
        logger.error(f"Error while uploading file {e}")
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,content={"Signals":ResponseSignal.FILE_NOT_SAVED.value})

    # store asset in DB
    asset_model = await AssetModel.create_instance(
        db_client=request.app.db_client,
    )

    asset_resource = Asset(
        asset_project_id=project.id,
        asset_type=AssetTypeEnum.FILE_.value,
        asset_name=file_id,
        asset_size=os.path.getsize(file_path),
    )

    asset_record = await asset_model.create_asset(asset=asset_resource)

    # print("#@#"*3)
    # print(asset_record)
    # print("#@#"*3)
     
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "Signals":ResponseSignal.FILE_UPLOADED_SUCCESSFULLY.value,
            "file_id": str(asset_record.id),
            "file_name": asset_record.asset_name,
            }
        )


# For process the file content and get content
@data_router.get("/process/{project_id}")
async def process_endpoint(request:Request,project_id:str, proecess_request:ProcessingRequest):
    file_id = proecess_request.file_id
    chunk_size = proecess_request.chunk_size
    overlap_size = proecess_request.overlap_size
    do_reset = proecess_request.do_reset


    project_model = await ProjectModel.create_instance(
        db_client=request.app.db_client
        )

    project = await project_model.get_project_or_create_one(project_id=project_id)
    asset_model = await AssetModel.create_instance(
        db_client=request.app.db_client
        )

    project_files_ids={}

    # if file_id is provided and send by user
    # we need to process that file only
    if proecess_request.file_id:
        asset_record = await asset_model.get_asset_record(
            asset_project_id=project.id,
            asset_name=proecess_request.file_id
            )

        if asset_record is None:
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"Signals":ResponseSignal.FILE_ID_NOT_FOUND.value})
       
        project_files_ids = {
            asset_record.id: asset_record.asset_name
        }
    
    # if file_id is not provided 
    # we need to get all files in the project
    # and process them
    else:
        # get the file project indexes
        project_files  = await asset_model.get_all_projects(
            asset_project_id=project.id,
            asset_type=AssetTypeEnum.FILE_.value
            )
        project_files_ids = {
            record.id: record.asset_name
            for record in project_files
        }

        if len(project_files_ids)==0:
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"Signals":ResponseSignal.NO_FILE_FOUND_IN_PROJECT.value})


    # create process controller
    # His mission is controll 
    process_controller = ProcessController(project_id=project_id)

    

    # create chunk model
    chunk_model = await ChunkModel.create_instance(db_client=request.app.db_client)

    # delete old chunks if do_reset is True
    if do_reset:
        await chunk_model.delete_chunks_by_project_id(project_id=project.id)

    no_records=0
    no_files=0
    # process each file (one by one file) from files that in project_files_ids
    # by chunking the file content
    # and store the chunks in the database
    # with also count no_chunks, no_files
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
                project_id=project_id,
                chunk_text=chunk.page_content,
                chunk_metadata=chunk.metadata,
                chunk_order=chunk_index+1,
                chunk_project_id=project.id,
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
