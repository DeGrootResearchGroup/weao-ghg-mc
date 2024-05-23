from scipy.optimize import minimize
from scipy.optimize import basinhopping
from scipy.stats import skewnorm
from scipy.stats import lognorm
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def pdf(x, a, loc, scale, dist):
    return -dist.pdf(x, a, loc, scale)


def fit_error(x, nominal, low, high, dist):
	# x[0] is the 'a' the parameter required for the selected distribution
	# x[1] is the 'loc' parameter scaled by the nominal value
	# x[2] is the 'scale' parameter scaled by the nominal value

	# Get the CDF values for the high and low values
	cdf = dist.cdf([low, high], x[0], loc=x[1]*nominal, scale=x[2]*nominal)

	# Get the mode of the PDF
	mode = minimize(pdf, nominal, args=(x[0], x[1]*nominal, x[2]*nominal, dist)).x[0]

	# Add a penalty if the 'a' parameter is negative
	penalty = x[0]**2 if x[0] < 0 else 0

	# Add a penalty if the PDF is flat around the nominal value
	if dist.pdf(nominal, x[0], loc=x[1]*nominal, scale=x[2]*nominal) < 1:
		penalty += 1

	# Add a penalty if the PDF is flat around the lower bound
	if dist.pdf(low, x[0], loc=x[1]*nominal, scale=x[2]*nominal) < 1e-3:
		penalty += 1

	# Return the error measure
	return (cdf[0] - 0.02)**2 + (cdf[-1] - 0.98)**2 + ((mode - nominal)/nominal)**2 + penalty


def solve_dist(nominal, low, high, dist, guess):
	# Initial guesses
	guess[1:2] = guess[1:2]/nominal

	# Solve global opimization and return distribution parameters
	res = basinhopping(fit_error, guess, niter=200, minimizer_kwargs={'method' : 'SLSQP', 'args' : (nominal, low, high, dist), 'tol' : 1e-7})
	return (res.x[0], res.x[1]*nominal, res.x[2]*nominal)


df = pd.read_excel('ParametersInput.xlsx')
for idx, row in df.iterrows():
	nominalValue = row['nominalValue']
	lowerBound = row['lowerBound']
	upperBound = row['upperBound']
	if row['distribution'] == 'lognorm':
		dist = lognorm
		guess = np.array([1, lowerBound, 0.25*(upperBound-lowerBound)])
	if row['distribution'] == 'skewnorm':
		dist = skewnorm
		guess = np.array([0, nominalValue, 0.25*(upperBound-lowerBound)])
	a, loc, scale = solve_dist(nominalValue, lowerBound, upperBound, dist, guess)
	df.loc[idx, 'distParam'] = a
	df.loc[idx, 'distLoc'] = loc
	df.loc[idx, 'distScale'] = scale
	cdf = dist.cdf([lowerBound, upperBound], a, loc=loc, scale=scale)
	mode = minimize(pdf, nominalValue, args=(a, loc, scale, dist)).x[0]
	df.loc[idx, 'distNominalValueError'] = mode - nominalValue
	df.loc[idx, 'distLowerBoundError'] = cdf[0] - 0.02
	df.loc[idx, 'distupperBoundError'] = cdf[1] - 0.98
	
	# Plot distribution
	fig, ax = plt.subplots(1, 1)
	x = np.linspace(max(lowerBound-(upperBound-lowerBound)*0.2, 0), upperBound+(upperBound-lowerBound)*0.2, 1000)
	ax.plot(x, dist.pdf(x, a, loc=loc, scale=scale), 'k-', lw=2, alpha=0.6)
	ax.plot([lowerBound, nominalValue, upperBound], dist.pdf([lowerBound, nominalValue, upperBound], a, loc=loc, scale=scale), 'ko', lw=2, alpha=0.6)
	ax.set_xlabel(row['parameter'])
	ax.set_ylabel('PDF')
	ax.set_ylim(bottom=0)
	plt.savefig('{}.png'.format(idx), bbox_inches='tight', dpi=300)

df.to_excel('ParametersDistributions.xlsx')
