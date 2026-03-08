from .BaseReport import BaseReport

class MissCover:
    def __init__(self, line : int, miss : int, total : int, extra : str = None):
        self.line = line
        self.miss = miss
        self.total = total
        self.extra = extra