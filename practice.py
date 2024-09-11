import datetime

import time

p1 = datetime.datetime.now()


time.sleep(30)


p2 = datetime.datetime.now()


print(p1)
print(p2)

print(p2-p1)