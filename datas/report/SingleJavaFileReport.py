from .BaseReport import BaseReport
from .MissCover import MissCover

class SingleJavaFileReport(BaseReport):
    def __init__(self, fileName : str, cover : int, total : int):
        super().__init__(cover, total)
        self.fileName = fileName
        self.missCovers : list[MissCover] = []

    def __dict__(self) -> dict:
        return {
            
        }