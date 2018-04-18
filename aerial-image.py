# -*- coding: utf-8 -*-
"""
Created on Thu Apr 4 18:34:12 2018

@author: Naveenkumar
"""

#imports added for the script
import urllib.request
import os
import sys
import shutil
import matplotlib.pyplot as plt
import numpy as np
import math

#Creation of folder
currDir = 'C:/Users/Naveenkumar/Desktop/Geo/Homework3/'
newFolder = currDir + 'images/'
shutil.rmtree(newFolder, ignore_errors=True)
os.mkdir(newFolder, 0o777)
         
#Function used to download tile putting them together and generating the image array
def getTile(x1, y1, x2, y2, level):
    imageArray = []
    for y in range(y1, y2+1):
        col = [] 
        for x in range(x1, x2+1):
                    quadKey = tileToQuadKey(x, y, level)
                    name = str(x % x1) + str(y % y1) + '.jpg'
                    val, msg = getImage(quadKey, name)              
                    if val == 0:
                        return imageArray, 1
                    if np.all((plt.imread(os.path.join(newFolder, name))) == getNullImage()) == True:    
                        return imageArray, 1
                    col.append(str(x % x1) + str(y % y1))
        imageArray.append(col)
    return imageArray, 0

#Function used to convert the tiles to it's corresponding quard keys
def tileToQuadKey(tileX, tileY, level):
    quadKey = ""
    for itertor in range(level, 0, -1):
        digit='0'
        maskPixel = (1 << (itertor - 1))
        if (tileX & maskPixel) != 0:
            digit = chr(ord(digit) + 1)          
        if (tileY & maskPixel) != 0:
            digit = chr(ord(digit) + 1)
            digit = chr(ord(digit) + 1)
        quadKey += digit
    return quadKey

#Function used to getthe image from Bing server
def getImage(quadKey, name): 
    img = os.path.join(newFolder, name)
    url = 'http://h0.ortho.tiles.virtualearth.net/tiles/h' + quadKey + '.jpeg?g=131&key=' + 'Al_51RNiQdqI-PuTU-DiZz4hoEzx_l9YtXj-RuR5FWV7CrduEoZOxQZBuKG9wlRq'
    try:
        urllib.request.urlretrieve(url, img)
    except:
        return 0
    return 1, 'success'

#Loading the null image for reference
def getNullImage():
    nullImg = os.path.join(currDir, 'null.jpg')
    nullObj = plt.imread(nullImg)
    return nullObj  

#Function used to check iif the axis is fine
def checkAxis(lat1, lon1, lat2, lon2, MaximumResolution):
    #Iterating through axis to calculate the no of tiles
    for index in range(MaximumResolution, 0, -1):        
        x1, y1 = latLongToTiles(lat1, lon1, index)
        x2, y2 = latLongToTiles(lat2, lon2, index)  
        #Interchanging Based on greater value
        if y1 > y2:
            y1, y2 = y2, y1                      
        if x1 > x2:
            x1, x2 = x2, x1       
        if (x2 - x1 >= 1) and (y2 - y1 >= 1):
            return x1, y1, x2, y2, index
    print ("Error with the Co-ordinates")
    sys.exit()

#Function used to convert latitude and longitude to tiles    
def latLongToTiles(latitude, longitude, level):
    xAxisPixel, yAxisPixel = CoordToPixel(latitude, longitude, level)
    tileX = int(xAxisPixel / 256)
    tileY = int(yAxisPixel / 256) 
    return tileX, tileY

#Function used to convert co-ordinates to it's corresponding pixel values
def CoordToPixel(latitude, longitude, level):
    #Comparing with minimum and maximum latitude and longitude values
    latitude = min(max(latitude, -85.05112878), 85.05112878)
    longitude = min(max(longitude, -180), 180)
    x = (longitude + 180) / 360
    sinLatitude = math.sin(latitude * math.pi / 180)
    y = 0.5 - math.log((1 + sinLatitude) / (1 - sinLatitude)) / (4 * math.pi)       
    mapsize = 256 << level
    xPixel = min(max(x * mapsize + 0.5, 0), mapsize - 1)
    yPixel = min(max(y * mapsize + 0.5, 0), mapsize - 1)
    return xPixel, yPixel

# Function used to create empty array and stitch images based on coordinates and display it
def startStitch(imageArray, folder):
    height, width = np.shape(imageArray)
    fileStack = np.zeros((height * 256, width * 256, 3), np.uint8)
    for iteration in range(len(imageArray)):
        imageStack = np.zeros((1 * 256, width * 256, 3), np.uint8)
        for secondIteration in imageArray[iteration]:
            img = plt.imread(folder + secondIteration + '.jpg')
            imageStack = np.hstack((imageStack, img))
        imageStack = imageStack[:, width * 256:, :3]
        fileStack = np.vstack((fileStack, imageStack)) 
    fileStack = fileStack[height * 256 : ,: , :3]
    baseFolder = os.path.split(os.path.abspath(folder))[0]
    plt.imsave(baseFolder + '/resultant_image.jpg', fileStack)
    return fileStack  

#Main function of our script	
def loadImage(latitudeOne, longitudeOne, latitudeTwo, longitudeTwo): 
    #Global variables
    MaximumResolution = 23
    validate = 1
    print("Program started please wait.........")
    #Looping through the co-ordinates    
    while (validate == 1):
        x1, y1, x2, y2, level = checkAxis(latitudeOne, longitudeOne, latitudeTwo, longitudeTwo, MaximumResolution)
        imageArray, validate = getTile(x1, y1, x2, y2, level)
        
        MaximumResolution = MaximumResolution -1
        if MaximumResolution < 0:
            break    
    finalResult = startStitch(imageArray, newFolder)
    print("........Displaying image.........")
    plt.imshow(finalResult)
    plt.show()

#Function which maeks the start of the script
if __name__ == '__main__':
    latitudeOne = input('Enter first latitude....: ')
    latitudeTwo = input('Enter first longitude....: ')
    longitudeOne = input('Enter second latitude....: ')
    longitudeTwo = input('Enter a second longitude...: ')
    #Calling the function to generate the aerial image
    loadImage(float(latitudeOne), float(latitudeTwo), float(longitudeOne), float(longitudeTwo))
    #loadImage(41.838928, -87.628503, 41.838244, -87.626847)