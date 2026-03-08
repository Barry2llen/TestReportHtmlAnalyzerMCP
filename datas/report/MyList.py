
class MyList(list):
    def __init__(self, *args, switchLines = 0, switchTable = 0, tableBlank = 4):
        super().__init__(*args)
        self.switchLines = switchLines
        self.switchTable = switchTable
        self.tableBlank = tableBlank

    @property
    def table(self):
        return self.tableBlank * ' '

    def __str__(self):
        res = self.switchLines * '\n' + self.switchTable * self.table
        for each in self:
            res += str(each) + ',' + self.switchLines * '\n' + self.switchTable * self.table
        res = res[:-(1 + self.switchLines + self.switchTable * len(self.table))]
        return f'[{res}\n{(self.switchTable - 1) * self.table if self.switchTable > 0 else ""}]'
