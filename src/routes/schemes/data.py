from pydantic import BaseModel
from typing import Optional

class ProcessingRequest(BaseModel):
    file_id: str =None
    chunk_size:Optional[int] = 1024
    overlap_size: Optional[int] =20
    reset :Optional[int] = 0
    do_reset: Optional[int] =0

