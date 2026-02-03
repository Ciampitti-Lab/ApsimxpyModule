from abc import ABC, abstractmethod

class ApsimModifier(ABC):
    @abstractmethod
    def _reload(self):
        pass
    @abstractmethod
    def save_changes(self):
        pass