from helpers import send_message, init_client_socket, discover_hosts
import threading



if __name__ == '__main__':
    [ip, port] = discover_hosts().split(' ')
    c_socket = init_client_socket(ip, port)

    send_mes_thread = threading.Thread(target=send_message, args=(c_socket, ))
    send_mes_thread.start()


    while True:
        data = c_socket.recv(1024)
        print(f'receive from server: { data.decode()}')