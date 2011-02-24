import socket
import time
import re
import sys
import string
from urlparse import urlparse

def main():
    if len(sys.argv) == 1:
        raise Exception("url is required")

    target_url = get_url(sys.argv[1])
    sock = get_socket_to_url(target_url)
    print fetch_content(sock)


def get_socket_to_url(target_url):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((target_url['host'], target_url['port']))
    sock.send('GET ' + target_url['path'] + ' ' + target_url['protocol'] +
    '/1.1\r\nHost:' + target_url['host'] + '\r\n\r\n')
    return sock


def get_url(unparsed_url):
    if re.search("//", unparsed_url) is None:
        unparsed_url = "//" + unparsed_url 
    parsed_result = urlparse(unparsed_url)
    url = {}
    url['host'] = parsed_result.netloc
    if parsed_result.path == "":
        url['path'] = "/"
    else:
        url['path'] = parsed_result.path
    if parsed_result.port is None:
        url['port'] = 80
    else:
        url['port'] = int(parsed_result.port)
    if parsed_result.scheme  == "":
        url['protocol'] = "HTTP"
    else:
        url['protocol'] = string.upper(parsed_result.scheme)
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
    header = {}
    for line in iter(lambda: get_line(sock), ''):
        line_items = line.split(': ')
        if len(line_items) == 1:
            header['status'] = line_items[0]
        else:
            header[string.lower(line_items[0])] = line_items[1]
    return header


def get_line(sock):
    line = ''
    for char in iter(lambda: sock.recv(1), '\r'):
        if ((char != '\n') and (char != '\r')):
            line += char
    return line


def get_status_code(header):
    if 'status' in header:
        matches = re.search("^HTTP/\d+\.\d+ (\d{3})", header['status'])
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
    if 'content-length' in header:
        return int(header['content-length'])
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
