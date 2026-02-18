from enum import Enum

class VectorDBEnums(Enum):
    QDRANT = "QDRANT"
    
class DistanceMetrics(Enum):
    COSINE = "COSINE"
    DOT = "DOT"
    EUCLIDEAN = "EUCLIDEAN"