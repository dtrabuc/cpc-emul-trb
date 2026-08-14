from abc import ABC, abstractmethod

class IODevice(ABC):
    @abstractmethod
    def read(self, port: int) -> int:
        pass

    @abstractmethod
    def write(self, port: int, value: int) -> None:
        pass