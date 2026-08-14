# Dans core/io_device.py
from abc import ABC, abstractmethod

class IODevice(ABC):
    @abstractmethod
    def read(self, port: int) -> int:
        pass

    @abstractmethod
    def write(self, port: int, value: int):
        pass

    @abstractmethod
    def is_active(self, port: int) -> bool:
        pass