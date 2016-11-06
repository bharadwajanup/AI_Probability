#!/usr/bin/python
#
# Mountain ridge finder
# Based on skeleton code by D. Crandall, Oct 2016

from PIL import Image
from numpy import *
from scipy.ndimage import filters
from scipy.misc import imsave
from heuristics import *
import random
from copy import deepcopy

import sys

# calculate "Edge strength map" of an image
#
def edge_strength(input_image):
    grayscale = array(input_image.convert('L'))
    filtered_y = zeros(grayscale.shape)
    filters.sobel(grayscale,0,filtered_y)
    return filtered_y**2

# draw a "line" on an image (actually just plot the given y-coordinates
#  for each x-coordinate)
# - image is the image to draw on
# - y_coordinates is a list, containing the y-coordinates and length equal to the x dimension size
#   of the image
# - color is a (red, green, blue) color triple (e.g. (255, 0, 0) would be pure red
# - thickness is thickness of line in pixels
#
def draw_edge(image, y_coordinates, color, thickness):
    for (x, y) in enumerate(y_coordinates):
        for t in range( max(y-thickness/2, 0), min(y+thickness/2, image.size[1]-1 ) ):
            image.putpixel((x, t), color)
    return image

# main program
#
(input_filename, output_filename, gt_row, gt_col) = ('test_images/mountain9.jpg','test_images/output.jpg', 3, 4)

# load in image
input_image = Image.open(input_filename)

# compute edge strength mask
edge_strength = edge_strength(input_image)
edgeStrength = deepcopy(edge_strength)
modifiedEdgeStrength = removeUseless(edgeStrength, int(len(edgeStrength) - round(0.2 * len(edgeStrength))))

row_index = edge_strength.argmax(axis=0)
imsave('edges.jpg', edge_strength)
minParameters = []
topEdgeVals = []
for i in range(len(modifiedEdgeStrength[0])):
    colState = []
    for eachrow in modifiedEdgeStrength:
        colState.append(eachrow[i])
    minMaxEdgeWeight, topVals = lowerRows(colState)
    minParameters.append(minMaxEdgeWeight)
    topEdgeVals.append(topVals)

for i in range(len(topEdgeVals)):
    colState = []
    for eachrow in modifiedEdgeStrength:
        colState.append(eachrow[i])

totalMatrix = []
for i in range(len(modifiedEdgeStrength[0])):
    eachCol = []
    columnValues = []
    for eachrow in modifiedEdgeStrength:
        columnValues.append(eachrow[i])
    for j in range(len(columnValues)):
        eachCol.append(columnValues[j]/sum(columnValues))
    totalMatrix.append(eachCol)

probabilityMatrix = transpose(totalMatrix)
modifiedProbStrength = removeUseless(probabilityMatrix, int(len(probabilityMatrix) - round(0.2 * len(probabilityMatrix))))

'''
for i in range(len(topEdgeVals)):
    for j in range(len(topEdgeVals[i])):
        if i < len(probabilityMatrix) - 1:
            #for ctr1 in range(len(probabilityMatrix[i+1])):
            print topEdgeVals[i][j], i+1, j, probabilityMatrix[i+1][j]
'''

def calcSamples(colNo, topEdgeVals):
    for eachVal in topEdgeVals:
        topEdgeVals1 = []
        for i in range(len(modifiedProbStrength)):
            if type(eachVal) is tuple:
                topEdgeVals1.append(
                    (i, formulaToCalculate(modifiedProbStrength[i][colNo], len(modifiedEdgeStrength), abs(eachVal[0] - i)), modifiedProbStrength[i][colNo]))
            else:
                topEdgeVals1.append(
                    (i, formulaToCalculate(modifiedProbStrength[i][colNo], len(modifiedEdgeStrength), abs(eachVal - i)), modifiedProbStrength[i][colNo]))
    return topEdgeVals1

returnedVal = calcSamples(1, topEdgeVals[0])

def bestReturnedVals(values):
    values.sort(key=lambda tup: tup[1])
    return values[-10:]

T = 10

allPossibleRidges = []

for t in range(1, T):
    finalRidgeList = []
    probCounter = []
    finalRidgeList.append(topEdgeVals[0][0])
    probCounter.append(0)
    if t != 1:
        returnedVal = calcSamples(1, topEdgeVals[0])
    for i in range(2, len(modifiedEdgeStrength[0])):
        bestVals = bestReturnedVals(returnedVal)
        returnedVal = calcSamples(i, bestVals)
        finalRidgeList.append(bestVals[-1][0])
        probCounter.append(bestVals[-1][2])

    allPossibleRidges.append((finalRidgeList, sum(probCounter)))

allPossibleRidges.sort(key=lambda tup: tup[1])
finalRidgeList = allPossibleRidges[-1][0]

# You'll need to add code here to figure out the results! For now,
# just create a horizontal centered line.
ridge = minParameters
ridge = finalRidgeList
# output answer
imsave(output_filename, draw_edge(input_image, ridge, (0, 0, 255), 5))
