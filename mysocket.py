import socket
import time
import re
import sys
import string


def main():
    sock = get_socket_to_url()
    print fetch_content(sock)


def get_socket_to_url():
    target_url = get_url(sys.argv)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #now connect to the web server on port 80
    # - the normal http port
    sock.connect((target_url['host'], target_url['port']))
    sock.send('GET ' + target_url['path'] + ' ' + target_url['protocol'] +
    '/1.1\r\nHost:' + target_url['host'] + '\r\n\r\n')
    return sock


def get_url(arguments):
    if len(arguments) == 1:
        raise Exception("url is required")
    m = re.match("((\w+)://)?([\w.]+)(:(\d+))?(/.*)?", arguments[1])
    protocol = m.group(2)
    host = m.group(3)
    port = m.group(5)
    path = m.group(6)
    url = {}
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


def fetch_content(sock):
    header = get_header(sock)
    status_code = get_status_code(header)
    if status_code < 200 or status_code > 299:
        return get_special_message(status_code)
    content_length = get_content_length(header)
    if content_length > 0:
        #full content chunk
        return safe_get(sock, content_length)
    # continue here, we are chunked into pieces
    # for now put loop here, extract out getting the count
    content = ""
    chunk_length = int(get_line(sock), 16)
    while (chunk_length > 0):
        content += safe_get(sock, chunk_length)
        chunk_length = int(find_next_non_empty_line(sock), 16)
    return content


def get_header(sock):
    header = []
    for line in iter(lambda: get_line(sock), ''):
        header.append(line)
    return header


def get_line(sock):
    line = ''
    for l in iter(lambda: sock.recv(1), '\r'):
        if ((l != '\n') and (l != '\r')):
            line += l
    return line


def get_status_code(header):
    for line in header:
        matches = re.search("^HTTP/\d+\.\d+ (\d{3})", line)
        if matches != None:
            return int(matches.group(1))
    return -1


def get_special_message(code):
    if code >= 300 and code < 400:
        return "Page has moved"
    elif code >= 400 and code < 500:
        return "Bad Request"
    elif code >= 500 and code < 600:
        return "Server Error"


def get_content_length(header):
    for line in header:
        if (re.match("Content-Length: \d+$", line)):
            return int(line[line.find(": ") + 2:len(line)])
    return -1


def find_next_non_empty_line(sock):
    line = ''
    while line == '':
        line = get_line(sock)
    return line


def safe_get(sock, content_length):
    get_length = 1024
    received = ''
    while (len(received) + get_length) < content_length:
        received += sock.recv(get_length)
    while len(received) < content_length:
        remaining = content_length - len(received)
        extra = sock.recv(remaining)
        received += extra
    return received


if __name__ == "__main__":
    main()
