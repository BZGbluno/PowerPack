import pandas as pd
import subprocess
from datetime import datetime
import matplotlib.pyplot as plt

# This will call the csv line remover, which removes the first 15 lines
#subprocess.run(["./csv-line-remover.sh"])

# This will read in the desired time chart reader
df = pd.read_csv('timechart1.csv')

# Dropping the Record Id label
df.drop('RecordId', axis=1, inplace=True)

# This will turn all the time stamps into date time objects
df['Timestamp'] = df['Timestamp'].apply(lambda x: datetime.strptime(x, '%H:%M:%S:%f'))

# retrieve the first time stamp
time0 = df['Timestamp'][0]

# subtract all the time stamps with the first one
df['Timestamp'] = df['Timestamp'].apply(lambda x: x - time0)

# plotting the amd u prof
df.plot(x='Timestamp', y='socket0-package-power', kind='line')

# Display the plot
plt.xlabel('Time')
plt.ylabel('Power Consumption')
plt.title('Power Consumption Over Time')
plt.grid(True)
plt.show()