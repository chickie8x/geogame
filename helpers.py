import threading
import socket
import time

BROADCAST_PORT_SERVER = 12349
BROADCAST_PORT_LB = 12348
IP = '127.0.0.1'

def create_server_socket(ip, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((ip, port))
    server_socket.listen()
    print(f'start listening on port {port}')
    return server_socket


def init_client_socket(ip, port):
    server_addr = (ip, int(port))
    c_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    c_socket.connect(server_addr)
    return c_socket





def handle_client(client_socket, addr):
    print(f'accepted connection from {addr}')
    # client_socket.send(bytes('connected successfully'.encode()))
    while True:
        data = client_socket.recv(1024)
        if not data:
            print('socket closed')
            break
        message = data.decode()
        print(f'receive from {addr} : {message}')
        client_socket.send(bytes(f'server reply: {message}'.encode()))
    client_socket.close()


def lb_handle_client(client_socket, addr, socket_list, leader_index):
    print(f'accepted connection from {addr}')
    client_socket.send(bytes('connected successfully'.encode()))
    while True:
        data = client_socket.recv(1024)
        if not data:
            print('socket closed')
            break
        message = data.decode()
        print(f'forward this to server: {message}')
        sock_index = leader_index
        success_forward = False
        while not success_forward:
            try:
                forward_socket = socket_list[sock_index]
                forward_socket.send(bytes(data))
                success_forward = True
            except:
                sock_index += 1
        success_forward = False
        res = forward_socket.recv(1024)
        client_socket.send(res)
    client_socket.close()


def listen_connection(socket):
    while True:
        client, addr = socket.accept()

        # start new thread to handle client 
        client_thread = threading.Thread(target=handle_client, args=(client, addr,))
        client_thread.start()


def send_message(socket):
    while True:
        message = input("Enter a message to send to the server (type 'exit' to close): ")
    
        if message.lower() == 'exit':
            break
        try:
            socket.send(message.encode())
        except:
            print('can not send mesage to server')
        time.sleep(0.2)
    socket.close()


def send_broadcast(addr, port_bind, target_port):
    broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    b_address = (IP, port_bind)
    broadcast_socket.bind(b_address)
    while True:
        message = bytes(addr, 'utf-8')
        broadcast_socket.sendto(message, ('255.255.255.255', target_port))
        time.sleep(4)


def discover_hosts():
    # Create a UDP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

    # Enable broadcasting mode
    client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    # Bind to a specific address and port
    client_socket.bind(('0.0.0.0', BROADCAST_PORT_LB))

    try:
        print("Listening for broadcasts...")
        while True:
            # Receive data
            data, addr = client_socket.recvfrom(1024)
            print(f"connecting to {data}")
            return data.decode()

    except:
        pass

    finally:
        client_socket.close()


def lb_discover_hosts(node_list, node_threads_list):
    # Create a UDP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

    # Enable broadcasting mode
    client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    # Bind to a specific address and port
    client_socket.bind(('0.0.0.0', BROADCAST_PORT_SERVER))

    try:
        print("Listening for broadcasts...")
        while True:
            # Receive data
            data, addr = client_socket.recvfrom(1024)
            if data.decode() not in node_list:
                node_list.append(data.decode())
                [ip, port] = data.decode().split(' ')
                node_thread = init_client_socket(ip, port) 
                node_threads_list.append(node_thread)
                print(node_threads_list)
    except:
        print('error occurs, can not listen to broadcast')


def lcr_vote(nodes):
    # The LCR (Leader, Circular, Right) Algorithm is a simple algorithm used to elect a leader in a distributed system.
    # Each participant (player) is initially assigned a unique identifier (e.g., player ID).
    # Participants are organized in a circular manner.
    # Participants pass a token (ID) with their vote to their right neighbor.
    # If a participant receives a vote, it compares its own ID with the received vote. If the received ID is greater, the participant passes the vote to its right neighbor. If the received ID is smaller, the participant discards the received vote.
    # If a participant has the highest ID among its neighbors, it becomes the leader.
    
    pass

