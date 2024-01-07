from helpers import IP, lb_discover_hosts, create_server_socket, lb_handle_client, send_broadcast,handle_client, BROADCAST_PORT_LB
import threading
import socket


node_list = []
node_socket_list = []
leader_node_socket_index = 0
lb_port = 12344
lb_broadcast_port = 12354
lb_addr = f'{IP} {lb_port}'



if __name__ == '__main__':

   # start listening broadcast from servers 
   broadcast_receive_thread = threading.Thread(target=lb_discover_hosts, args= (node_list, node_socket_list)) 
   broadcast_receive_thread.start()

   #start sending broadcast to client
   broadcast_sending_thread = threading.Thread(target=send_broadcast, args=(lb_addr, lb_broadcast_port, BROADCAST_PORT_LB ))
   broadcast_sending_thread.start()


   lb_socket = create_server_socket(IP, lb_port)

   while True:

      client, addr = lb_socket.accept()

      # Start a new thread to handle the client
      client_thread = threading.Thread(target=lb_handle_client, args=(client, addr, node_socket_list, leader_node_socket_index))
      client_thread.start()




    
   
    