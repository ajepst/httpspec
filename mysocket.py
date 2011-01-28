import socket
import time
import re

s = socket.socket ( socket.AF_INET, socket.SOCK_STREAM)
#now connect to the web server on port 80
# - the normal http port
#s.connect(("www.slicehost.com", 80))
s.connect(("www.foofish.org", 80))
s.send('GET / HTTP/1.1\r\nHost:www.foofish.org\r\n\r\n')
#s.send('GET / HTTP/1.1\r\nHost:www.slicehost.com\r\n\r\n')

#data = s.recv(100)

#print data
#fullString = data

#while data: 
    #    starttime = time.time()
#    data = s.recv(3000)
    #    fullString += data
#    print data
    #print "received %d bytes in %d secs " %(len(data),time.time()-starttime) 
#    data =  s.recv(100)
#s.close()
#print fullString[:512] 

#for c in iter(lambda: f.read(1),'\n'):
#        pass

def getLine(s):
    line = '' 
    for l in iter(lambda: s.recv(1), '\r'):
        if ((l != '\n') and (l != '\r')):
            line += l
    return line

def getHeader(s):
    header =[] 
    for line in iter(lambda:getLine(s), ''):
        header.append(line) 
    #    print line 
    return header

def getContentLength(header):
    for line in header: 
        if (re.match("Content-Length: \d+$", line)):
            return int(line[line.find(": ")+2 : len(line)])
    return -1

def findNextNonEmptyLine(s):
    line = ''
    while line == '':
        line = getLine(s)
    return line

def safeGet(s, contentLength):
    getLength = 1024
    received ='' 
    while (len(received) + getLength) < contentLength:
        received += s.recv(getLength)
    remaining = contentLength - len(received)
    received += s.recv(remaining)
    return received

def fetchContent(s):

    header = getHeader(s)
    contentLength = getContentLength(header)   
    if contentLength > 0:
        #full content chunk
        return safeGet(s, contentLength)
    # continue here, we are chunked into pieces
    # for now put loop here, extract out getting the count 
    content = ""
    chunkLength = int(getLine(s), 16)
    while (chunkLength > 0):
        content += safeGet(s, chunkLength)
        chunkLength = int(findNextNonEmptyLine(s), 16)
    return content 
 

print fetchContent(s) 
