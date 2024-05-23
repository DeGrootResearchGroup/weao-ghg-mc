from scipy.stats import skewnorm
from scipy.stats import lognorm
import numpy as np
import pandas as pd

df_in = pd.read_excel('ParametersDistributions.xlsx', index_col=0)

data = {}
for idx, row in df_in.iterrows():
	if row['distribution'] == 'lognorm':
		dist = lognorm
	if row['distribution'] == 'skewnorm':
		dist = skewnorm
	a = row['distParam']
	loc = row['distLoc']
	scale = row['distScale']
	lowerBound = row['lowerBound']
	upperBound = row['upperBound']
	samples = []
	while len(samples) < 10000:
		samples_req = 10000-len(samples)
		new_samples = dist.rvs(a, loc=loc, scale=scale, size=samples_req)
		new_samples = new_samples[new_samples > lowerBound]
		new_samples = new_samples[new_samples < upperBound]
		samples.extend(new_samples.tolist())
	data[str(idx)] = np.array(samples)

df = pd.DataFrame.from_dict(data)
df.to_excel('RandomSamples.xlsx')