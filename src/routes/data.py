from fastapi import FastAPI,APIRouter, Depends,UploadFile,status
from fastapi.responses import JSONResponse
import os
from helpers.config import get_settings,Settings
from controllers import DataController,ProjectController,ProcessController
import aiofiles
from models import ResponseSignal
import logging
from .schemes.data import ProcessingRequest


logger = logging.getLogger("uvicorn.error")

data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["data"]
)

@data_router.get("/upload/{project_id}")
async def upload_data(project_id:str ,file:UploadFile ,
                      app_settings: Settings = Depends(get_settings)):
    # Validata the file properties
    data_controller = DataController()
    is_valid,result_Signals = data_controller.validate_uploaded_file(file=file)

    if not is_valid:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"Signals":result_Signals})
    
    project_dir_path = ProjectController().get_project_path(project_id=project_id)
    file_path, file_id  = data_controller.generate_unique_filepath(
        orig_file_name=file.filename,
        project_id=project_id
    )

    try:
        async with aiofiles.open(file_path, "wb") as f:
            while chunk := await file.read(app_settings.FILE_DEFAULT_CHUNK_SIZE):
                await f.write(chunk)
    except Exception as e:
        logger.error(f"Error while uploading file {e}")
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,content={"Signals":ResponseSignal.FILE_NOT_SAVED.value})


    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "Signals":ResponseSignal.FILE_UPLOADED_SUCCESSFULLY.value,
            "file_id": file_id,
            }
        )




@data_router.get("/process/{project_id}")
async def process_endpoint(project_id:str, proecess_request:ProcessingRequest):
    file_id = proecess_request.file_id
    chunk_size = proecess_request.chunk_size
    overlap_size = proecess_request.overlap_size
    process_controller = ProcessController(project_id=project_id)
    file_content = process_controller.get_file_content(file_id=file_id)
    
    file_chunks = process_controller.process_file_content(
        file_content=file_content,
        file_id=file_id,
        chunk_size=chunk_size,
        overlap_size=overlap_size
    )
    if file_chunks is None or len(file_chunks) == 0:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"Signals":ResponseSignal.PROCESSING_FAILED.value})

    return file_chunks
