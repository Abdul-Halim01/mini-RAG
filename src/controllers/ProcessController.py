from .BaseController import BaseController
from .ProjectController import ProjectController
from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders import PyMuPDFLoader
from models import ProcessingEnum
from langchain_text_splitters import CharacterTextSplitter
import os



class ProcessController(BaseController):
    """
    Controller responsible for handling project file processing.

    Main responsibilities:
    - Locate project files using the project ID.
    - Detect file type and select the appropriate loader.
    - Load file content from supported formats (TXT, PDF).
    - Split file content into smaller chunks for downstream processing
      such as indexing, embedding, or retrieval tasks.
    """

    def __init__(self,project_id:str):
        """
        Initialize the controller with a specific project context.

        Args:
            project_id (str): Unique identifier of the project whose
                              files will be processed.
        """

        super().__init__()
        self.project_id = project_id
        self.project_path = ProjectController().get_project_path(project_id=project_id)

    def get_file_extension(self,file_id:str):
        """
        Extract the file extension from a file identifier or filename.

        Args:
            file_id (str): File name or identifier.

        Returns:
            str: File extension including the dot (e.g., '.txt', '.pdf').
        """
        return os.path.splitext(file_id)[-1]
    
    def get_file_loader(self,file_id):
        """
        Determine the correct loader for a file based on its extension.

        Supported types:
        - TXT files using TextLoader
        - PDF files using PyMuPDFLoader

        Args:
            file_id (str): File name or identifier.

        Returns:
            Loader instance or None:
                Returns a loader object if supported and file exists,
                otherwise None.
        """

        file_ext = self.get_file_extension(file_id=file_id)
        file_path = os.path.join(
            self.project_path,
            file_id
        )

        if not os.path.exists(file_path):
            return None

        if file_ext == ProcessingEnum.TXT.value:
            return TextLoader(file_path,encoding="utf-8")
        
        if file_ext == ProcessingEnum.PDF.value:
            return PyMuPDFLoader(file_path)
        
        print(f"Unsupported file type: {file_ext}")
        return None
    
    def get_file_content(self, file_id:str):
        """
        Load file content using the appropriate loader(from get_file_loader method of this class).

        Args:
            file_id (str): File name or identifier.

        Returns:
            list or None:
                Loaded document records if successful,
                otherwise None if unsupported or missing.
        """
        loader = self.get_file_loader(file_id=file_id)
        if loader is None:
            return None
        
        return loader.load()

    def process_file_content(self,file_content:list,file_id,
                            chunk_size: int=100,overlap_size: int=20):
        """
        Split loaded file content into smaller text chunks.

        Useful for NLP pipelines such as embeddings, semantic search,
        or retrieval augmented generation.

        But i will focus in my Project on RAG(retrieval augmented generation)

        Args:
            file_content (list): Loaded document objects.
            file_id (str): Identifier of the file being processed.
            chunk_size (int, optional): Maximum size of each chunk.
                                        Default is 100.
            overlap_size (int, optional): Overlap between chunks to
                                         preserve context. Default is 20.

        Returns:
            list: List of chunked document objects with metadata preserved.
        """
        
        text_splitter = CharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=overlap_size,
            length_function=len,
        )
        # print("#########")
        # print("file_content: ",file_content)
        # print("#########")
        
        file_content_texts =[
            rec.page_content
            for rec in file_content
        ]
        

        file_content_metadata =[
            rec.metadata
            for rec in file_content
        ]
        
        chunks = text_splitter.create_documents(
            file_content_texts,
            metadatas=file_content_metadata
            )

        return chunks