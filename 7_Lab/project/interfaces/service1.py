from abc import ABC, abstractmethod

class IInterface1(ABC):
    @abstractmethod
    def operation1(self) -> str:
        pass