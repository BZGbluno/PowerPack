from TimeSync.client import CalibrationTools
import subprocess
import time
import pdb
import os
SERVER_IP = '127.0.0.1'
SERVER_PORT = 25565

def start_server(ip, port):
    """Start the server process."""
    os.chdir("C:\\Users\\iambr\\PowerPack\\PowerPack\\TimeSync")
    print(os.getcwd())
    return subprocess.Popen(
        ['python3', 'server.py', str(ip), str(port)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True  # This makes stdout and stderr strings instead of bytes
    )

def read_server_output(proc):
    """Read and print the server's output and error streams after termination."""
    stdout, stderr = proc.communicate()  # Read stdout and stderr
    if stdout:
        print("Server Output:\n", stdout)
    if stderr:
        print("Server Error:\n", stderr)

def stop_server(proc):
    """Terminate the server process gracefully."""
    try:
        proc.terminate()  # Request termination
        proc.wait(timeout=5)  # Wait for server to shut down gracefully
    except subprocess.TimeoutExpired:
        proc.kill()  # Force kill if timeout expired

def main():
    # Start the server
    server_proc = start_server(SERVER_IP, SERVER_PORT)

    # Give the server a moment to start up
    time.sleep(2)

    # Create and use CalibrationTools client
    test = CalibrationTools(SERVER_IP, SERVER_PORT)
    try:
        results = test.timeCalibration(1)
        print(f"Offset and Round Trip Delay: {results}")
    except Exception as e:
        print(f"Error during calibration: {e}")

    # Stop the server
    stop_server(server_proc)

    # Read and print the server's output and error streams after shutdown
    #pdb.set_trace()
    read_server_output(server_proc)

if __name__ == "__main__":
    main()
