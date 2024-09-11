import socket
import time
import pandas as pd
import numpy as np
import struct



class CalibrationTools:
    '''
    This is a calibration tool that will be used to synchronize 2 systems. It
    will achieve this by either using CPU burn or a protocol that I made that is 
    similiar to the NTP protocol
    '''

    def __init__(self, serverIP, serverPort):
        '''
        This will set the Server IP and Server Port. It will also initialize
        an array that will store the time data
        '''
        self.allTimes = []
        self.SERVER_IP = serverIP
        self.SERVER_PORT = serverPort


    def _measure(self, ip, port, rounds:int):
        '''
        This will ping time between the client and server a "rounds" amount of 
        times. It will will append each round as a row into the allTimes array

        t0: Client time sending
        t1: Server time
        t3: Client time recieving
        '''

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            
            
            # connect with the server
            client_socket.connect((ip, port))
            print(f"Connected to {ip}:{port}")

            # turn off nagles algorithm
            client_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, True)

            # loop for pinging a rounds amount of times
            for _ in range(0, rounds):
                
                # current round sample
                sample = []
                

                t0 = time.time()
                client_socket.sendall(b'T')
                
                # 8 bytes because floating point number
                t1 = client_socket.recv(8)
                t3 = time.time()
                t1 = struct.unpack('d', t1)[0]

                # save all data
                sample.append(t0)
                sample.append(t1)
                sample.append(t3)

                #print(sample)
                self.allTimes.append(sample)



    def timeCalibration(self, rounds: int):
        '''
        This will call the _measure() method to recieve all the pinging time
        data. It will then clean all the data by using IQR. It will then return
        the mean offset that reprsents the time client needs to change in order to 
        be synchronized with the server
        '''


        # call to measure
        self._measure(self.SERVER_IP, self.SERVER_PORT, rounds)


        # turn into numpy array
        matrix = np.array(self.allTimes)
        
        # make into data frame for easier data manipulation
        df = pd.DataFrame(matrix, columns = ['t0','t1','t3'])
        
        #removing outliers using IQR
        for col in df.columns:

            Q1 = np.percentile(df[col], 25)
            Q3 = np.percentile(df[col], 75)
            IQR = Q3 - Q1

            lowerBound = Q1 - 1.5 * IQR
            upperBound = Q3 + 1.5 * IQR
            df[col] = np.where((df[col] < lowerBound) | (df[col] > upperBound), np.nan, df[col])

        df = df.dropna()

        #round Trip delay column
        df['roundTripDelay'] = ((df['t3'] - df['t0']))

        #offset column
        df['offset'] = ((df['t1'] - df['t0']) + (df['t1'] - df['t3']))/2
        
        # find mean roundTrip delay
        roundTripDelay = float(df['roundTripDelay'].mean())

        # find the mean offset
        offset =float(df['offset'].mean())
        print(df)
        return offset, roundTripDelay
    

    def cpuBurnCalibration():
        '''
        This method will find where the CPU started using more power by 
        looking at a table of values and find the time where the time increased
        '''
        print("hi")


if __name__ == "__main__":

    # SERVER_IP = "127.0.0.1" # refers to your own machine 
    #SERVER_IP = '127.0.0.1'
    #SERVER_IP = "172.29.176.187"
    #SERVER_IP = '172.29.214.199'
    SERVER_IP = '10.42.0.66'
    SERVER_PORT = 25565
    test = CalibrationTools(SERVER_IP, SERVER_PORT)
    offset, delay = test.timeCalibration(1000)
    print(f'This value describe how to change client clock to synchronize with server {offset}\n and this is the round trip delay {delay}')


