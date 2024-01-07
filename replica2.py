import threading
import time
from helpers import create_server_socket, listen_connection, send_broadcast, IP

server_port = 12342
server_broadcast_port = 12352

node_addr = f'{IP} {server_port}'


if __name__ == '__main__':

    # sending broadcast 
    send_broadcast_thread = threading.Thread(target=send_broadcast, args=(node_addr,server_broadcast_port))
    send_broadcast_thread.start()

    # creating server threads 
    server = create_server_socket(IP, server_port)
    t = threading.Thread(target=listen_connection, args=(server,))
    t.start()

    
    