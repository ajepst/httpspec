import socket
import time
import re
import sys
import string

def geturl(arguments):
    if len(arguments) == 1:
       raise Exception("url is required")
    m = re.match("((\w+)://)?([\w.]+)(:(\d+))?(/.*)?", arguments[1])
    protocol = m.group(2)
    host = m.group(3)
    port = m.group(5)
    path = m.group(6)
    url =  {}
    if protocol != None:
        url['protocol'] = string.upper(protocol)
    else:
        url['protocol'] = "HTTP"
    if port != None:
        url['port'] = int(port)
    else:
        url['port'] = 80
    if path != None:
        url['path'] = path
    else:
        url['path'] = "/"
    url['host'] = host
    return url 


targeturl = geturl(sys.argv)

s = socket.socket ( socket.AF_INET, socket.SOCK_STREAM)
#now connect to the web server on port 80
# - the normal http port
s.connect((targeturl['host'], targeturl['port']))
s.send('GET ' + targeturl['path'] + ' ' + targeturl['protocol'] + '/1.1\r\nHost:' + targeturl['host'] + '\r\n\r\n')

def getLine(s):
    line = '' 
    for l in iter(lambda: s.recv(1), '\r'):
        if ((l != '\n') and (l != '\r')):
            line += l
    return line

def getHeader(s):
    header = [] 
    for line in iter(lambda:getLine(s), ''):
        header.append(line) 
    #    print line 
    return header

def getContentLength(header):
    for line in header: 
        if (re.match("Content-Length: \d+$", line)):
            return int(line[line.find(": ")+2 : len(line)])
    return -1

def getStatusCode(header):
    for line in header:
        matches = re.search("^HTTP/\d+\.\d+ (\d{3})", line)
        if matches != None:
            return int(matches.group(1)) 
    return -1

def findNextNonEmptyLine(s):
    line = ''
    while line == '':
        line = getLine(s)
    return line

def safeGet(s, contentLength):
    getLength = 1024
    received = '' 
    while (len(received) + getLength) < contentLength:
        received += s.recv(getLength)
    while len(received) < contentLength: 
        remaining = contentLength - len(received)
        extra = s.recv(remaining)
        received += extra
    return received

def getSpecialMessage(code):
    if code >= 300 and code < 400:
        return "Page has moved"
    if code >= 400 and code < 500:
        return "Bad Request" 
    if code >= 500 and code < 600:
        return "Server Error"

def fetchContent(s):

    header = getHeader(s)
    statusCode = getStatusCode(header)
    if statusCode != 200:
        return getSpecialMessage(statusCode)
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
