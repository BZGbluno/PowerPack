import socket
import signal
import sys
import time
import struct

def start_server(ip, port):
    '''
    This will start the server that will be pinged by the client
    to send over it system time.
    '''
    # the .AF_INET will represent that the socket will say the socket being used is the IPv4
    # the .SOCK_STREAM will represent that the socket wil be a TCP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # the server will listen to incoming connections with IP and port
    server_socket.bind((ip, port))
    # Turns the socket into listening mode, the param represents the amount of connections
    server_socket.listen(1)
    # The max amount of queued connections for the server
    server_socket.settimeout(1)
    print(f"Server started at {ip}:{port}, waiting for connections...",flush=True)
    # handles the SIGINT signal which is made when pressing crtl +c
    def signal_handler(sig, frame):
        print("\nServer shutting down.")
        server_socket.close()
        sys.exit(0)
    
    # registers the signal_handler functions and when ctrl+c is pressed the signal handler will be called
    signal.signal(signal.SIGINT, signal_handler)
    


    # the server will always run unless crtl+c is pressed or an error that isn't time out occurs
    while True:
        try:
            # accepts new connections
            client_socket, client_address = server_socket.accept()
        except socket.timeout:
            continue
        
        # turn off nagles algorithm
        client_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, True)
        
        # with the client
        with client_socket:
            



            while True:
                
                data = client_socket.recv(1)
                if not data:
                    print("ended pining")
                    sys.exit(0)
                t1 = struct.pack('d', time.time())
                #print(t1,flush=True)
                client_socket.sendall(t1)
                #print(f"Message sent to {ip}:{port}",flush=True)


# if __name__ == "__main__":

#     if len(sys.argv) < 3:
#         print("More parametesr needed")
#         sys.exit(1)
    
#     SERVER_IP = sys.argv[1]
#     SERVER_PORT = sys.argv[2]


#     # SERVER_IP = '127.0.0.1' 
#     # SERVER_PORT = 25565
#     start_server(SERVER_IP, int(SERVER_PORT))


#SERVER_IP = '127.0.0.1' 
SERVER_IP = '10.42.0.66'
#SERVER_IP = '10.42.0.1' 
SERVER_PORT = 25565
start_server(SERVER_IP, SERVER_PORT)