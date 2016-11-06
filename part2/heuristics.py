import numpy as np
'''
array = np.array([1, 30, 15, 2, 25])
print array.argsort()[-3:]
print min(array.argsort()[-3:])
'''
def lowerRows(edgeStrength):
    array = np.asarray(edgeStrength)
    topValues = array.argsort()[-45:]
    return min(topValues), topValues

def adjacentCols(prevCol, nextCol):
    #Idea is that the rows should not be same for adjacent pixels
    print ""

def calcDist(a, b):
    return np.linalg.norm(a - b)

def dist(var1, list2):
    print var1
    for item in list2:
        print item
    print "--------"


def formulaToCalculate(probScore, numberofRows, rowDiff):
    return (probScore * numberofRows) / (1 + rowDiff)

