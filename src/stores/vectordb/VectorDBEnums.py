from enum import Enum

class VectorDBEnums(Enum):
    QDRANT = "QDRANT"
    PGVECTOR = "PGVECTOR"
    
class DistanceMethodEnums(Enum):
    COSINE = "COSINE"
    DOT = "DOT"
    EUCLIDEAN = "EUCLIDEAN"

class PgVectorTableSchemaEnums(Enum):
    ID = "id"
    TEXT = "text"
    CHUNK_ID = "chunk_id"
    VECTOR = "vector"
    METADATA = "metadata"
    _PREFIX = "pgvector"

    
class PgVectorDistanceMethodEnums(Enum):
    COSINE = "vector_cosine_ops"
    DOT = "vector_12_ops"

class PgVectorIndexTypeEnums(Enum):
    IVFFLAT = "ivfflat"
    HNSW = "hnsw"
    