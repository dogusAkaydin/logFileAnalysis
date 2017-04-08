#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

def parseLogFile(inFileName):
    import re
    allData = []
    with open(inFileName) as inFile:
        for line in inFile:
            line=re.split(r'“|”|"',line,flags=re.UNICODE)
            line0=line[0].split()
            line1=line[1].split()
            line2=line[2].split()
            #If 'HTTP/1.0' is missing from the request 
            #then fill with '-'
            if len(line1)!=3:
               line1.append('-') 
            line = [line0,line1,line2]
            line = [item for sublist in line for item in sublist]
            allData.append(line)
    
    return allData

if __name__ == '__main__':
    print ('Please import this script in another script \
            instead of executing it directly.')

