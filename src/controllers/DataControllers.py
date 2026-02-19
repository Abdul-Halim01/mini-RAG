from .BaseController import BaseController
from fastapi import UploadFile
from models import ResponseSignal
from .ProjectController import ProjectController
import re
import os

class DataController(BaseController):
    """
    Controller responsible for handling uploaded file management.

    Main responsibilities:
    - Validate uploaded files against allowed types and size limits.
    - Generate unique file paths for project-specific uploads.
    - Clean and normalize file names for safe filesystem storage.
    """
    def __init__(self):
        """
        Initialize the DataController.

        Sets the size conversion factor used to compare file size
        limits (MB to bytes).
        """
        super().__init__()
        self.size_scale=1048576 # convert MB to Bytes
    
    def validate_uploaded_file(self,file:UploadFile):
        """
        Validate an uploaded file based on type and size constraints.

        Args:
            file (UploadFile): File received from the upload request.

        Returns:
            tuple:
                (bool, str)
                - Validation status (True if valid, False otherwise).
                - Response signal indicating validation result.
        """

        if file.content_type not in self.app_settings.FILE_ALLOWED_TYPES:
            return False,ResponseSignal.FILE_TYPE_NOT_SUPPORTED.value
        
        if file.size > self.app_settings.FILE_MAX_SIZE* self.size_scale:
            return False,ResponseSignal.FILE_SIZE_EXCEEDED.value
        
        return True,ResponseSignal.SUCCESS.value
    
    def generate_unique_filepath(self,orig_file_name:str,project_id:str):
        """
        Generate a unique file path for storing an uploaded file.

        Ensures:
        - File name is cleaned from unsafe characters.
        - File path is unique inside the project directory.

        Args:
            orig_file_name (str): Original uploaded file name.
            project_id (str): Identifier of the associated project.

        Returns:
            tuple:
                (full_file_path, new_file_name)
                - Absolute path where the file should be saved.
                - Generated unique filename.
        """
        random_filename = self.generate_random_string()
        project_path = ProjectController().get_project_path(project_id=project_id)

        cleaned_file_name = self.get_clean_file_name(orig_file_name=orig_file_name)
        
        random_key  = self.generate_random_string()
        
        new_file_path = os.path.join(project_path,random_key+'_'+cleaned_file_name)
       
        while os.path.exists(new_file_path):
            random_key  = self.generate_random_string()
            new_file_path = os.path.join(project_path,
                                         random_key+'_'+cleaned_file_name
                                        )


        return new_file_path, random_key + "_" + cleaned_file_name

    def get_clean_file_name(self, orig_file_name: str):
        """
        Clean a file name by removing unsafe characters and normalizing it.

        Operations performed:
        - Remove special characters except underscores and dots.
        - Trim surrounding whitespace.
        - Replace spaces with underscores.

        Args:
            orig_file_name (str): Original file name.

        Returns:
            str: Cleaned file name with only safe characters.
        """
        # remove any special characters, except underscore and .
        cleaned_file_name = re.sub(r'[^\w.]', '', orig_file_name.strip())

        # replace spaces with underscore
        cleaned_file_name = cleaned_file_name.replace(" ", "_")

        return cleaned_file_name