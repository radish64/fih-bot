import tokenize
import re

class fihfile:
    def __init__(self, f):
        self.data = []
        file = open(f,"r")
        for line in file:
            #print(line)
            self.data.append(re.split(':|,', line.rstrip()))
        #print(self.data)
    def getCategory(self, category):
        for f in self.data:
            if (f[0] == category):
                return f[1:]
