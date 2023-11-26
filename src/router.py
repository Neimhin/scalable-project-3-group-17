'''
CONTRIBUTORS: NAARORA
'''

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional
from typing import TypedDict
from typing import Optional

class FIBEntry(TypedDict):
    hop: int
    interested_key_name: str
    created_at: float

class Router(ABC):
    
    @abstractmethod
    def create_fib_entry(self, data_name: str, hop: int, interested_key_name: str) -> None:
        pass

    @abstractmethod
    def get_fib_entry(self, data_name: str) -> Optional[FIBEntry]:
        pass

    @abstractmethod
    def update_fib_entry(self, data_name: str, hop: int, interested_key_name: str) -> None:
        pass

class BasicRouter(Router):
    def __init__(self):
        self.FIB: dict[str, FIBEntry] = {}

    def create_fib_entry(self, data_name: str, hop: int, interested_key_name: str) -> None:
        entry: FIBEntry = {
            'hop': hop,
            'interested_key_name': interested_key_name,
            'created_at': datetime.now().timestamp()
        }
        self.FIB[data_name] = entry

    def get_fib_entry(self, data_name: str) -> Optional[FIBEntry]:
        return self.FIB.get(data_name)

    def update_fib_entry(self, data_name: str, hop: int, interested_key_name: str) -> None:
        if data_name in self.FIB:
            self.FIB[data_name]['hop'] = hop
            self.FIB[data_name]['interested_key_name'] = interested_key_name

