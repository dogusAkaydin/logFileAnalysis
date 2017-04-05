#! /usr/bin/env python
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

import sys
import os
import numpy

def parseLogFile(inFileName):
    allData = []
    with open(inFileName) as inFile:
        for line in inFile: 
            data=line.split()
            allData.append(data)
    
    return allData

if __name__ == '__main__':
    print ('Please import this script in another script \
            instead of executing it directly.')

