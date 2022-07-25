from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

owid_url = 'https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv'

df = pd.read_csv(owid_url)

# filtering for Nepal data
npl = df[df['iso_code'] == 'NPL']

# converting string type to datetime
npl['date'] = pd.to_datetime(npl['date'])

smoothed_cases = []
for date in sorted(npl['date']):
    npl['gkv'] = np.exp(
        -(((npl['date'] - date).apply(lambda x: x.days)) ** 2) / (2 * (2 ** 2))
    )
    npl['gkv'] /= npl['gkv'].sum()
    smoothed_cases.append(round(npl['new_cases'] * npl['gkv']).sum())

print(npl['gkv'])
npl['smoothed_new_cases'] = smoothed_cases
plt.plot(npl['date'],npl['smoothed_new_cases'])
plt.savefig('test.png',bbox_inches='tight')
