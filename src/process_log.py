#! /usr/bin/env python
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
import sys
import time
import datetime
import functions

def main(logPath,hostsPath,hoursPath,resourcesPath,blockedPath):
    start = time.time()
    print "Parsing the log file ..."
    parsedData = functions.parseLogFile(logPath)
    end = time.time()
    print 'Done with parsing the log file in %i seconds.' % (end-start)

#    This is how the data looks like after parsing:
#    hosts      = [row[0] for row in parsedData]    
#    timeStamps = [row[3] for row in parsedData]    
#    timeZones  = [row[4] for row in parsedData]    
#    requests1  = [row[5] for row in parsedData]    
#    requests2  = [row[6] for row in parsedData]    
#    requests3  = [row[7] for row in parsedData]    
#    replies    = [row[8] for row in parsedData]    
#    bytes      = [int(row[-1]) for row in parsedData]    

#Hosts:
    print 'Working on Feature 1 ...'
    start = time.time()
    oFile = open(hostsPath,'w')     
    #Sort based on host name
    sortedData = sorted(parsedData, key=lambda x: x[0])
    hosts      = [row[0] for row in sortedData]    
    iBeg    = []
    rowPre  = []
    sumBytes = []
    hits = []
    #Log the indexes where host name changes
    for i, row in enumerate(sortedData):
        if (row[0] != rowPre):
            iBeg.append(i)
            rowPre = row[0]

    #Subtract consequtive list elements to find 
    #the number of hits by each host.  
    hits = [j-i for i,j in zip(iBeg[:-1], iBeg[1:])] 

    #Sort the number of hits in relation with host name indices
    hitsSorted, iBegSorted = (list(i) for i in 
                zip(*sorted(zip(hits, iBeg), reverse=True)))
    #Print the first 10
    for i in range(0,9):
        print >> oFile, "%s, %s" % (hosts[iBegSorted[i]], 
                                    hitsSorted[i])

    oFile.close()
    end = time.time()
    print 'Done with Feature 1 in an additional %i seconds.' % (
                                                      end-start)

#Resources:
    print 'Working on Feature 2 ...'
    start = time.time()
    oFile = open(resourcesPath,'w') 
    #Sort based on resource path:
    sortedData = sorted(parsedData, key=lambda x: x[6])
    requests2  = [row[6] for row in sortedData]    
    bytes = []

    for row in sortedData:
        try: 
            bytes.append(int(row[-1]))
        #Byte field may be '-'
        except ValueError:
            bytes.append(0)

    iBeg    = []
    rowPre  = []
    sumBytes = []    
    #Log the indexes where resource path changes
    for i, row in enumerate(sortedData):
        if (row[6] != rowPre):
            iBeg.append(i)
            rowPre = row[6]

    #Sum the number of bytes sent from each resource path 
    for i in range(0,len(iBeg)-1):
        sss = sum(bytes[iBeg[i]:iBeg[i+1]])   
        sumBytes.append(sss)   

    #Sort the number of bytes in relation with resource paths
    sumBytesSorted, iBegSorted = (list(i) for i in 
                zip(*sorted(zip(sumBytes, iBeg), reverse=True))) 
    
    #Print the first 10   
    for i in range(0,9):
        print >> oFile, "%s, %d" % (requests2[iBegSorted[i]], 
                                    sumBytesSorted[i])

    oFile.close()
    end = time.time()
    print 'Done with Feature 2 in an additional %i seconds.' % (end-start)

#Hours
    print 'Working on Feature 3 ...'
    start = time.time()
    oFile = open(resourcesPath,'w') 
    timeStamps = [row[3][1:] for row in parsedData]    
    times = []
    #Convert timeStamps to datetime objects
    for t in timeStamps:
        times.append(datetime.datetime.strptime(t,'%d/%b/%Y:%H:%M:%S'))

    hits  = []
    iCuts = []
    iBase = 0
    tBase = times[0]
    tCut  = tBase     
    tEnd  = times[-1]
    while tCut <= tEnd: #Don't exceed the latest time in file
        #Set cut-off time 60 mins ahead
        tCut = tBase+datetime.timedelta(minutes=60)
        #Scan from the base time (times[iBase]) onwards
        #(No need to scan the past)
        for i, t in enumerate(times[iBase:]):
            #Log when you reach or first exceed the cut-off time
            if t >= tCut:
                iCuts.append(iBase+1)
                hits.append(i)  #Num. of hits from tBase to tCut
                iBase = iBase+i #Update the cut-off index
                tBase = t #Update the base time
                break

    #Sort the number of hits in relation with cut-off indices
    hitsSorted, iCutsSorted = (list(i) for i in 
                   zip(*sorted(zip(hits, iCuts), reverse=True))) 

    #Print the first 10
    for i in range(0,9):
        print >> oFile, "%s, %d" % (times[iCutsSorted[i]], hitsSorted[i])

    oFile.close()
    end = time.time()
    print 'Done with Feature 3 in an additional %i seconds.' % (end-start)

#Blocked
    print 'Working on Feature 4 ...'
    start = time.time()
    hosts      = [row[0]      for row in parsedData] 
    timeStamps = [row[3][1:]  for row in parsedData] 
    requests   = [row[6][0:6] for row in parsedData] 
    replies    = [row[8]      for row in parsedData] 
    times = []
    oFile = open(blockedPath,'w')     
    #Convert timeStamps to datetime objects
    for t in timeStamps:
        times.append(datetime.datetime.strptime
                                       (t, '%d/%b/%Y:%H:%M:%S'))
    #Start a watchlist with its first row being empty entries
    #host, tFirstAttempt, NumberOfAttempts, isBlocked, 'tBlock'
    watchlist = ([[' ' , ' ' , ' ', ' ', ' ']])  
    for i, t in enumerate(times):
        isLogin = (requests[i] == '/login')
        goodLogin = (isLogin and replies[i] == '200')
        failLogin = (isLogin and not(replies[i] == '200'))
        r = 0
        while True:
            if hosts[i] ==  watchlist[r][0]: #If in the watchlist
                isBlocked = watchlist[r][3]  # = 1 if blocked
                tBlock    = watchlist[r][4]  # time of block 
                if isBlocked:
                    if isinstance(tBlock,str):
                        tBlockStr = tBlock
                    else:
		        tBlockStr = tBlock.strftime(
                                    '%d/%b/%Y:%H:%M:%S')
                    lt5min = ( (t-tBlock) <= 
                               datetime.timedelta(minutes=5))
                    if lt5min: 
                    #Log all these hits that would have been 
                    #blocked 
                        #Recover the unparsed format 
                        print >> oFile, "%s" % ( 
                                     parsedData[i][0]+' ' +
                                     parsedData[i][1]+' ' +
                                     parsedData[i][2]+' ' +
                                     parsedData[i][3]+' ' +
                                     parsedData[i][4]+' "'+
                                     parsedData[i][5]+' ' +
                                     parsedData[i][6]+' ' +
                                     parsedData[i][7]+'" '+
                                     parsedData[i][8]+' ' +
                                     parsedData[i][9])
                    else: #5 min. past since the block
                          #Remove it from the watchlist 
                          #(no history, no block)
                        del watchlist[r]
                    break #to check the next hit
                elif failLogin:
                    #Not yet blocked but getting close!
                    #Increase failed attemp count by one
                    watchlist[r][2] += 1 
                    #Was its first fail less than 20 sec. ago?
                    tFirstAttempt = watchlist[r][1]
                    lt20sec = ( (t - tFirstAttempt) <= 
                                datetime.timedelta(seconds=20) )
                    #Is this its 3rd attempt yet?
                    is3attempts = (watchlist[r][2] == 3)
                    if lt20sec:
                        if is3attempts:
                            #Block the host and ...
                            watchlist[r][3] = 1 
                            #... log the blocking time.
                            watchlist[r][4] = t 
                    else:
                        #Infrequent login failure 
                        #not getting watched.
                        #Remove it from the wathchlist 
                        #(no history, no block)
                        del watchlist[r]
                    #Watchlist is updated according to the rules.
                    break #to check the next hit
                elif goodLogin:
                    #Successful login while in watchlist 
                    #but not blocked.  
                    #Remove it from the wathchlist 
                    #(no history, no block)
                    del watchlist[r]
                    break #to check the next hit
            else: #Not yet seen in the watchlist
                if failLogin:
                #Keep checking the rest of the watchlist
                    r += 1 
                    if r == len(watchlist): 
                    #Not found in watchlist
                        #Create the watchlist entry and break 
                        #for checking the next hit
                        watchlist.append([hosts[i],t,1,0,'-'])
                        break
                elif goodLogin or not(isLogin): 
                    #Nothing wrong with this hit
                    #No need to check the rest of the watchlist
                    break #to check the next hit
    oFile.close()
    end = time.time()
    print 'Done with Feature 4 in an additional %i seconds.' % (end-start)

    return

#-----------------------------------------------------------
if __name__ == '__main__':
    logPath        = sys.argv[1]
    hostsPath      = sys.argv[2]
    hoursPath      = sys.argv[3]
    resourcesPath  = sys.argv[4]
    blockedPath    = sys.argv[5]
    main(logPath,hostsPath,hoursPath,resourcesPath,blockedPath)

