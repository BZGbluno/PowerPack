import socket
import signal
import sys
import subprocess
import json
import time

def reader(file):
    '''
    The goal of this function is to read times written to file 
    by the subprocess function. It then returns this dictionary
    to be used by the client
    '''
    with open(file, 'r') as f:
        data = json.load(f)
    print(data)
    print(type(data))
    return data


def start_server(ip, port):
    '''
    This function will run the server forever unless it recieves a SIGint 
    signal which is caused by "ctrl + c". The purpose of this server is to
    connect with the client and run a class using subprocess. Once a client is
    connected, it send a "process beginning" to indicate initial measurements. 
    Once the subprocess is complete, it sends a "Process finished" message. Finally, 
    the server sends a dictionary that contains the possbile code wrap arounds.
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
    print(f"Server started at {ip}:{port}, waiting for connections...")

    # handles the SIGINT signal which is made when pressing crtl +c
    def signal_handler(sig, frame):
        print("\nServer shutting down.")
        server_socket.close()
        sys.exit(0)
    
    # registers the signal_handler functions and when ctrl+c is pressed the signal handler will be called
    signal.signal(signal.SIGINT, signal_handler)
    
    # server runs forever unless ctrl+c is pressed
    while True:
        try:
            # accepts new connections
            client_socket, client_address = server_socket.accept()
        except socket.timeout:
            continue
        with client_socket:

            # Connection established
            print(f"Connection from {client_address} established.")
            processStarting = "Process Starting"
            
            # Process Starting message being sent
            client_socket.sendall(processStarting.encode('utf-8'))

            # Running the class
            began = str(time.time())

            # simulate work being done
            time.sleep(10)
            
            # Process Finished message being sent
            processComplete = "Process finished"
            ended = str(time.time())
            client_socket.sendall(processComplete.encode('utf-8'))
            
            # Array that contains when the work began and ended
            times = [began, ended]

            # Sending over the information
            client_socket.sendall(times.encode('utf-8'))

            client_socket.close()


SERVER_IP = "172.29.176.187"
SERVER_PORT = 25565      

start_server(SERVER_IP, SERVER_PORT)
