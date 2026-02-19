from .BaseController import BaseController
from fastapi import UploadFile
from models import ResponseSignal
import os

class ProjectController(BaseController):
    """
    Controller responsible for managing project file storage.

    Main responsibilities:
    - Create and manage project-specific directories.
    - Provide filesystem paths for storing project files.
    - Ensure required directories exist before file operations.
    """

    def __init__(self):
        """
        Initialize the ProjectController.

        Inherits base configuration (such as file storage directory)
        from BaseController.
        """
        super().__init__()
    
    def get_project_path(self,project_id:str):
        """
        Get the absolute filesystem path for a project directory.

        Creates the directory if it doesn't exist.

        Args:
            project_id (str): Unique identifier of the project.

        Returns:
            str: Absolute path to the project directory.
        """
        project_dir = os.path.join(
            self.file_dir,
            project_id
        )
        if not os.path.exists(project_dir):
            os.makedirs(project_dir)

        return project_dir

