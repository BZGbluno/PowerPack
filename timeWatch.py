import sys
import time
import json
args = sys.argv

if len(args) != 2:
    print("not enough arguments available")
    sys.exit(1)

tiempo = args[1]
print("In time")

# represents the function
time.sleep(int(tiempo))
times = {2:"Step 1", 3: "step 2"}

with open('output.txt', 'w') as f:
    json.dump(times, f)