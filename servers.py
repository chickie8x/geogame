import threading
import time
from helpers import create_server_socket, listen_connection, send_broadcast, IP, BROADCAST_PORT_SERVER

server_port = 12340
broadcast_port_bind = 12350

node_addr = f'{IP} {server_port}'


if __name__ == '__main__':

    # sending broadcast 
    send_broadcast_thread = threading.Thread(target=send_broadcast, args=(node_addr,broadcast_port_bind, BROADCAST_PORT_SERVER))
    send_broadcast_thread.start()

    # creating server threads 
    server = create_server_socket(IP, server_port)
    t = threading.Thread(target=listen_connection, args=(server,))
    t.start()

    
    
