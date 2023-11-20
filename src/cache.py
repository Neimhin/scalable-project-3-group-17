# Define FIB, PIT, CS datastores

class CACHEStore:
    def __init__(self) -> None:
        self.CS_store = {}

    def get_store(self) -> dict:
        return self.CS_store