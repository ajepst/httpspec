import socket
import time
import re

s = socket.socket ( socket.AF_INET, socket.SOCK_STREAM)
#now connect to the web server on port 80
# - the normal http port
s.connect(("www.slicehost.com", 80))
#s.connect(("www.foofish.org", 80))
#s.send('GET / HTTP/1.1\r\nHost:www.foofish.org\r\n\r\n')
s.send('GET / HTTP/1.1\r\nHost:www.slicehost.com\r\n\r\n')

#data = s.recv(100)

#print data
#fullString = data

#while data: 
#    starttime = time.time()
#data = s.recv(500)
#    fullString += data
#print data
    #print "received %d bytes in %d secs " %(len(data),time.time()-starttime) 
#    data =  s.recv(100)
#s.close()
#print fullString[:512] 

#for c in iter(lambda: f.read(1),'\n'):
#        pass

def getLine(s):
    print "getline"
    line = '' 
    for l in iter(lambda: s.recv(1), '\r'):
        if ((l != '\n') and (l != '\r')):
            line += l
    return line

def getHeader(s):
    header =[] 
    for line in iter(lambda:getLine(s), ''):
        header.append(line) 
    return header

def getContentLength(header):
    for line in header: 
        if (re.match("Content-Length: \d+$", line)):
            return int(line[line.find(": ")+2 : len(line)])
    return -1

def safeGet(s, contentLength):
    chunkLength = 1024
    received ='' 
    while (len(received) + chunkLength) < contentLength:
        chunk = s.recv(chunkLength)
        received += chunk
    remaining = contentLength - len(received)
    received += s.recv(remaining)
    return received

def fetchlines(s):

    header = getHeader(s)
    contentLength = getContentLength(header)   
    if contentLength > 0:
        #full content chunk
        print "BELOW"
        return safeGet(s, contentLength)


    print "in fetchlines"
    myline = ''
    data = s.recv(2000)
    bytecount = 0 
    inheader = True 
    allContent = False
    readyToCount = False
    runningTotal = 0
    linesToReturn = "" 
    skipNextLine = False
    firstGroup = True

    

    while data:
        if '\n' in data:
             lines = data.split("\r\n")
             print "linecount: " + str(len(lines)) 
        for index, line in enumerate(lines):
            # print line
             if readyToCount and skipNextLine == False:
                 runningTotal += len(line)
                 print "total " + str(runningTotal) 
                 linesToReturn += line + "\r\n"
             if skipNextLine == True:
                 skipNextLine = False
             if inheader:
                 print "LINE is: [" + line+"]"
                 if (re.match("Content-Length: \d+$", line)):
                      # bytecount is the number above, not chunked
                      bytecount = int(line[line.find(": ")+2 : len(line)], 16)
                      print "LINE------------------>" +str(bytecount)
                      allContent = True
                      readyToCount = True
             if (allContent==False and readyToCount == False):
                 print "looking for bytecount"
                 if firstGroup and (len(line) == 0):
                     byteLine = lines[index + 1]
                     print "next line: " + str(byteLine)
                     inheader = False
                     firstGroup = False
                 elif not firstGroup:
                     byteLine = line 
                     print "followup byte count" + byteLine
                 else:
                     byteLine = ""
                 if (re.match("\d+", byteLine)):
                     # looks like we're chunked
                     bytecount = int(byteLine, 16) 
                     print "chunk size is |" + str(bytecount) + "|"
                     if bytecount == 0:
                         return linesToReturn
                     readyToCount = True
                     skipNextLine = True
                     #get the number of bytes above and then look again
             if (runningTotal >= bytecount) and inheader == False:
                print "over bytecount " + str(runningTotal)
                readyToCount = False 
                runningTotal = 0
                if allContent == True:
                     return linesToReturn
        data = s.recv(2000)
    return linesToReturn
print fetchlines(s) 
