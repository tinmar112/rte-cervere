import numpy as np
import pandas as pd

chemin = '//nashdprdif274/SMB_DTS-DAS/DTS/RAW/.DAEDL91TOURB/Positive/2023/2023-01-02-19-52-31.txt'

date = pd.to_datetime(chemin.strip('.txt')[-19:], format='%Y-%m-%d-%H-%M-%S').tz_localize('UTC')

with open (file=chemin, mode='r') as f:
    lines = f.readlines()
distances, temps = lines[8], lines[10]

distances = distances.replace(',','.').strip('\n').split(';')[1:]
temps = temps.replace(',','.').strip('\n').split(';')[1:]

df = pd.DataFrame(data={'KP': distances, 'temperature': temps}, dtype=np.float32)
df.insert(loc=0, column='time', value=np.full(shape=(df.shape[0],), fill_value=date))

print(df.head())
print(df.dtypes)