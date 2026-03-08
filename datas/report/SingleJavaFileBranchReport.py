from .SingleJavaFileReport import SingleJavaFileReport
from .MissCover import MissCover

class SingleJavaFileBranchReport(SingleJavaFileReport):
    def __init__(self, fileName : str, cover : int, total : int):
        super().__init__(fileName, cover, total)
        self.missedCovers : list[MissCover] = []

    def missCover2str(self, missCover : MissCover):
        return f'Line {missCover.line}:  {missCover.miss} of {missCover.total} branches missed'

    def __dict__(self):
        return {
            "fileName": self.fileName,
            "coverage": f'{self.cover / self.total * 100:.2f}%',
            "missedCovers": [self.missCover2str(item) for item in self.missedCovers]
        }