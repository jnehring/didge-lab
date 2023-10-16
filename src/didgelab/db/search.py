import os
import jsonlines

class DDBReader:

    def __init__(self, filters=[]):
        self.filters = filters

    def copy(self):
        return DDBReader(filters=self.filters)

    def iterate(self, path="../../didge-database/database_0.jsonl"):
        with jsonlines.open(path) as reader:
            for o in reader:
                ok=True
                for f in self.filters:
                    if not f(o):
                        ok=False
                        break
                if ok:
                    yield o

    def fundamental(self, note):
        self.filters.append(lambda x : x["fundamental_note_number"] == note)
        return self
    
import matplotlib.pyplot as plt
if __name__ == "__main__":

    ddb = DDBReader().fundamental(-29)
    i=0
    l = []
    for didge in ddb.iterate():
        l.append(didge["length"])
    plt.boxplot(l)
    plt.show()
    