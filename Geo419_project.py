# -*- coding: utf-8 -*-
"""
Created on Fri Nov  1 10:14:56 2019
Updated on Fri Jan 17 13:46:31 2020

@author: Patrick Fischer
"""

"""
Next to Do!
-  Regex genauer spezifizieren x

-- GUI? For setting the Workdirectory and the searched depth x?
"""
## Load packages
import os
import io
import re
import glob
import shutil
import csv
from geojson import Point, Feature, FeatureCollection, dump

## Set Working Directory
#os.chdir('C:/Users/Patrick/Desktop/Geo419_Projekt/')
#header = 'Header/'
os.chdir('E:/Material_GEO419/')
header = 'Headerfiles_Data_seperate_files_header_20140401_20191015_6179_v3V1_20191015/'
## Create new Folder
newDir = 'Filtered_Data'

if not os.path.exists(newDir):
    os.mkdir(newDir)
    print("Directory " , newDir ,  " Created ")
else:    
    print("Directory " , newDir ,  " already exists")

## Find Data which matters and copy it into the new Folder

 
## List .stm data    ! 
listOfFiles = [f for f in glob.glob(header + "**/*_sm_*.stm", recursive=True)]


#searched_depth = input('Input the searched depth in meters : ')
searched_depth = "0.05"
regex = r".+\d{1,2}\.\d+\s+" + re.escape(searched_depth)

## find all Data with "0.00    0.05" in first line. !
## copy data to 'Filtered_Data' !
def filter_files(file_name, regex):
    checked_file = open(file_name)
    first = checked_file.readline()
#    print(first)
    if re.match(regex, first):
        shutil.copy2(file_name, 'Filtered_Data')
#        print("Found!")
#    else:
#        print("Not Found!")
        
## Loop this through all subdirectories in the Working_Directory !
for i in listOfFiles:
    filter_files(i,regex)
    

listOfCopies = [f for f in glob.glob(newDir + "**/*.stm", recursive=True)]

def get_info_from_file(filename):
    '''
    @author: Christoph Paulik & Philip Buttinger
    ISMN Package: https://github.com/TUW-GEO/ismn
    '''
    with io.open(filename, mode='r', newline=None) as f:
        header = f.readline()
    header_elements = header.split()

    path, filen = os.path.split(filename)
    filename_elements = filen.split('_')

    return header_elements, filename_elements

coords = []
station = []
features = []

for i in listOfCopies:
    checked_file_1 = open(i)
    header_elements, filename_elements = get_info_from_file(i)
    coords.append(header_elements[3] + "/" + header_elements[4])
    station.append(header_elements[1] + "-" + header_elements[2] + "-" + header_elements[8])
    point = Point((float(header_elements[3]), float(header_elements[4])))
    features.append(Feature(geometry=point))

feature_collection = FeatureCollection(features)

with open('coordinates_2.geojson', 'w') as fb:
   dump(feature_collection, fb)
             
with open('stations.csv', 'w') as csvfile:
    filewriter = csv.writer(csvfile, delimiter=',')
    filewriter.writerow(coords)
    filewriter.writerow(station)        


