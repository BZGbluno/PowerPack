import time
import socket
import json
import random

# Network setup
SERVER_IP = "127.0.0.1"  # Localhost
SERVER_PORT = 25565

def send_data_to_server():
    counter = 0
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((SERVER_IP, SERVER_PORT))
            while True:  # Run indefinitely
                # Generate random voltage values between 0 and 3.3 volts
                voltage_before = round(random.uniform(0, 3.3), 2)
                voltage_after = round(random.uniform(0, 3.3), 2)

                # Create a voltage data packet
                voltage = [voltage_before, voltage_after]
                
                # Send the voltage reading to the server
                s.sendall(json.dumps(voltage).encode('utf-8'))
                print("Simulated voltage measured and sent:", voltage)
                counter = counter + 1
                time.sleep(0.01)  # Adjust the sleep time based on your needs
    except KeyboardInterrupt:
        print("Test client stopped.")
        print(f"Client sent {counter} packets!")

send_data_to_server()
