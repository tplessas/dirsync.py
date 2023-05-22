from abc import ABC, abstractmethod

class Repository(ABC):
    '''Abstract repository class.'''

    @abstractmethod
    def update_status(self):
        pass