from abc import ABC
import inspect

class Plugin(ABC):
    @classmethod
    def name(cls):
        return cls.__name__
    
    def relevent(self):
        return True
    
    def display(self) -> str:
        return None