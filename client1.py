from helpers import send_message, init_client_socket, discover_hosts
import threading
import pickle

username = {'username':None}

if __name__ == '__main__':
    [ip, port] = discover_hosts().split(' ')
    c_socket = init_client_socket(ip, port)

    send_mes_thread = threading.Thread(target=send_message, args=(c_socket, username))
    send_mes_thread.start()


    while True:
        try:
            data = c_socket.recv(1024)
            if not data:
                print('socket closed')
            res = pickle.loads(data)
            if res['command'] == 'setuser':
                username['username'] = pickle.loads(data)['params']
            else:
                print(f'\n{res["content"]}\n')

        except ConnectionResetError as e:
            print(e)
            break
    c_socket.close()
    exit()