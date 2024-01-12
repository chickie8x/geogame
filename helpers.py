import json
import threading
import socket
import time
import random
import csv
import pickle


BROADCAST_PORT_SERVER = 12349
BROADCAST_PORT_LB = 12348
IP = '127.0.0.1'
game_id = {'game_id': None}

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




# node handle clients
def handle_client(client_socket, addr):
    print(f'accepted connection from {addr}')
    while True:
        try:
            data = client_socket.recv(1024)
            if not data:
                print('socket closed')
                break
            message = pickle.loads(data)

            #handle messages 
            print(f'receive from {addr} : {message}')

            if message['command'] == 'creategame':
                game = create_game(message['params'])
                client_socket.send(pickle.dumps(game))
                game_start(questions['easy'], client_socket)
            elif message['command'] == 'answer':
                client_socket.send(pickle.dumps({ 'command':'response', 'params':{'username':message['params']['username'],'content':message['params']['content']}}))

        except ConnectionResetError as e:
            print(e)
            break
    client_socket.close()


# loadbalancer handle client
def lb_handle_client(client_socket, addr, message_queue, users):
    print(f'accepted connection from {addr}')

    username = f"user{random.randint(1000,2000)}"
    users[username] = client_socket
    client_socket.send(pickle.dumps({'command':'setuser', 'params':username}))

    #when number of clients >= 3 , send command start the game 
    if len(users) >= 3 and game_id['game_id'] is None:
        username_list = [name for name in users.keys()]
        message_queue.append({'command': 'creategame', 'params': username_list})

    while True:
        try: 
            data = client_socket.recv(1024)
            if not data:
                print('socket closed')
                break
            message_queue.append(pickle.loads(data))
            # message = data
            # print(f'forward this to server: {message}')
            # sock_index = leader_index
            # success_forward = False
            # while not success_forward:
            #     try:
            #         forward_socket = socket_list[sock_index]
            #         forward_socket.send(bytes(data))
            #         success_forward = True
            #     except:
            #         sock_index = leader_vote(len(socket_list))
            # success_forward = False

        except ConnectionResetError as e:
            print(e)
            break
    client_socket.close()


def handle_client_queue(cmes_queue, node_socket):
    while True:
        if len(cmes_queue) >0:
            mes = cmes_queue.pop(0)
            node_socket.send(pickle.dumps(mes))
            

def handle_server_queue(smes_queue, users):
    while True:
        if len(smes_queue) >0:
            mes = smes_queue.pop(0)
            print(mes)
            if mes['command'] == 'gamecreated':
                game_id['game_id'] = mes['params']['game_id']
                print(game_id)
            elif mes['command'] == 'response':
                c_socket = users[mes['params']['username']]
                c_socket.send(pickle.dumps({'command':'concac','content': mes['params']['content']}))
            elif mes['command'] == 'sendall':
                for user in users.keys():
                    c_socket = users[user]
                    c_socket.send(pickle.dumps({'command':'sendall','content': mes['params']}))


def send_message(socket, username):
    while True:
        s = input("Enter a message to send to the server (type 'exit' to close): ")
    
        if s.lower() == 'exit':
            break
        try:
            message = pickle.dumps({'command':'answer','params':{'username':username['username'], 'content':s}})
            socket.send(message)
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


def lb_discover_hosts(node_list, node_threads_list, leader_index):
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
                leader_index = leader_vote(node_threads_list.__len__())
    except:
        print('error occurs, can not listen to broadcast')


# listen to node message
def lb_listen_to_node(node_list, index, s_queue):
    while True:
        socket = node_list[index['index']]
        data = socket.recv(1024)
        if not data:
            print('socket closed')
        s_queue.append(pickle.loads(data))



# LRC voting 
class LCRLeaderElection:
    def __init__(self, num_nodes):
        self.num_nodes = num_nodes
        self.identifiers = [random.randint(1, 100) for _ in range(num_nodes)]
        self.leader = None
        self.election_lock = threading.Lock()

    def start_election(self):
        with self.election_lock:
            self.leader = 0
            for i in range(self.num_nodes):
                if self.identifiers[i] >= self.identifiers[self.leader]:
                    self.leader = i
            return self.leader


def leader_vote(num_nodes):
    election = LCRLeaderElection(num_nodes)
    return election.start_election()


# processing csv data
questions = {'easy':[], 'medium':[], 'hard':[]}

with open('question.csv', 'r', encoding='utf8') as f:
    csv_reader = csv.reader(f, delimiter=',')
    keys = []
    for idx, item in enumerate(csv_reader):
        if idx == 0:
            keys = item
        else:
            obj = dict(zip(keys, item))
            questions[item[1]].append(obj)



# create_game function that return game ID
def create_game(players):
    game_id = random.randint(1000, 2000)
    with open('gamestate.json', 'w') as f:
        game_state = {}
        game_state['game_id'] = game_id
        game_state['scores'] = {}
        for player in players:
            game_state['scores'][player] = 0
        json.dump(game_state, f)
    return {'command': 'gamecreated', 'params': {'game_id': game_id}}

# start the game 
def game_start(questions, lb_socket):
    lb_socket.send(pickle.dumps({'command':'sendall', 'params':"***GAME'S STARTING, GET READY***\nYou have 10s for each question"}))
    time.sleep(3)
    for question in questions:
        lb_socket.send(pickle.dumps({'command': 'sendall', 'params':question['question']}))
        time.sleep(2)
