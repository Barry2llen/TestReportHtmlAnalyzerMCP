
class MutationMissCover:
    def __init__(self, line : int, misses : list[str]):
        self.line = line
        self.misses = misses

    def __str__(self):
        description = ''
        for miss in self.misses:
            description += miss + ';'
        description = description[:-1]
        return f'At line {self.line}, {len(self.misses)} mutation misses, mutators:[{description}]'