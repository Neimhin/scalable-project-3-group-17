# Define FIB, PIT, CS datastores

class CACHEStore:
    def __init__(self) -> None:
        self.CIS = {}
        self.FIB = {}
        self.PIT = {}

    def get_CIS(self) -> dict:
        return self.CIS

    def get_FIB(self) -> dict:
        return self.FIB
    
    def get_PIT(self) -> dict:
        return self.PIT
