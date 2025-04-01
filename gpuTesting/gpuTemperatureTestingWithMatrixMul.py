import subprocess
import time
# The goal here is to run this forever until an error is returned from the subprocess
count:int = 0
startTime = time.time()
allTimes = []
while True:

    #This will run the matrix multiplication for 10 times

    roundStartTime = time.time() - startTime
    print(roundStartTime)
    for x in range(0,10):
        print("ex")
        
    
        result = subprocess.run(['./matrixMul', '-wA=1024', '-wB=1024', '-hA=1024', '-hB=1024'])
        print("2")
        if result.returncode != 0:
            
            print("This command failed")
            print(f'This is the amount of completed round of matrix mult: {count}')
            endStartTime  = time.time() - startTime
            allTimes.append([roundStartTime, endStartTime])
            print(allTimes)
            exit()
    
    endStartTime  = time.time() - startTime
    # to keek track of the amount of matrix multiplcation that system
    # can take before failing    
    count += 1
    print(count)
    allTimes.append([roundStartTime, endStartTime])
    print(allTimes)
    time.sleep(15)


