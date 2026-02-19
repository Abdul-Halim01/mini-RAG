from abc import ABC , abstractclassmethod
from typing import List,Dict,Any
from models.db_schemas import RetrieveDocument


class VectorDBInterface(ABC):

    @abstractclassmethod
    def connect(self):
        pass

    @abstractclassmethod
    def disconnect(self):
        pass

    @abstractclassmethod
    def is_collection_existed(self,collection_name:str)-> bool:
        pass
    
    @abstractclassmethod
    def list_all_collections(self)-> list:
        pass
    
    @abstractclassmethod
    def get_collection_info(self,collection_name:str) -> dict  :
        pass
    @abstractclassmethod
    def delete_collection(self,collection_name:str) :
        pass
    
    @abstractclassmethod
    def create_collection(self,collection_name:str,
                                embedding_size:int,
                                do_reset:bool = None):
        pass

    @abstractclassmethod
    def insert_one(self,collection_name:str,text:str, vector: List,
                        metadata: dict =None,
                        record_id:str = None):
        pass

    @abstractclassmethod
    def insert_many(self,collection_name:str,texts:List[str], 
                        vectors:List,metadata:List=None,
                        record_ids:List=None,batch_size:int=None):
        pass

    @abstractclassmethod
    def search_by_vector(self,collection_name:str,
                              vector:List,
                              limit:int)-> List[RetrieveDocument]:
        pass