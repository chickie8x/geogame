import socket
import threading
from helpers import create_socket

server_ports = [12340, 12341, 12342]
server_ip = '127.0.0.1'




if __name__ == '__main__':
    for port in server_ports:
        create_socket(server_ip, port)
