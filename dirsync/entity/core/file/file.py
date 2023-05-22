from abc import ABC, abstractmethod

class File(ABC):
    '''Abstract file class.'''

    @abstractmethod
    def calculate_blake2b_hash(self):
        pass