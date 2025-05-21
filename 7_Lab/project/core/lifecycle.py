from enum import Enum

class LifeStyle(Enum):
    PER_REQUEST = "PerRequest"
    SCOPED = "Scoped"
    SINGLETON = "Singleton"