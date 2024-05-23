import numpy as np
import pandas as pd
import seaborn as sns
from scipy.stats import bootstrap
import matplotlib.pyplot as plt

sns.set_style('white')
sns.set_palette('pastel')

nominal_vals = {
	'processN2O_aerobic' : 10332,
	'processCH4_aerobic' : 1236,
	'fugitiveN2O_discharge' : 209,
	'fugitiveCH4_discharge' : 296
}

df = pd.read_excel('SimulationResults.xlsx', index_col=0)
df['totalN2O'] = df['processN2O_aerobic'] + df['fugitiveN2O_discharge']
df['totalCH4'] = df['processCH4_aerobic'] + df['fugitiveCH4_discharge']
df['total'] = df['totalN2O'] + df['totalCH4']

median_cis = {
	'processN2O_aerobic' : bootstrap((df['processN2O_aerobic'].to_list(),), np.median).confidence_interval,
	'processCH4_aerobic' : bootstrap((df['processCH4_aerobic'].to_list(),), np.median).confidence_interval,
	'fugitiveN2O_discharge' : bootstrap((df['fugitiveN2O_discharge'].to_list(),), np.median).confidence_interval,
	'fugitiveCH4_discharge' : bootstrap((df['fugitiveCH4_discharge'].to_list(),), np.median).confidence_interval,
	'totalN2O' : bootstrap((df['totalN2O'].to_list(),), np.median).confidence_interval,
	'totalCH4' : bootstrap((df['totalCH4'].to_list(),), np.median).confidence_interval,
	'total' : bootstrap((df['total'].to_list(),), np.median).confidence_interval,
}

def plot_histogram(df, x, y=None, stat='probability', bins='auto', kde=True, legend=False, ax=None):
	return sns.histplot(data=df, x=x, y=y, stat=stat, bins=bins, kde=kde, ax=ax)

fig, axs = plt.subplots(nrows=2, ncols=2, sharey='all')
plot_histogram(df, 'processN2O_aerobic', bins=25, ax=axs[0,0])
plot_histogram(df, 'processCH4_aerobic', bins=25, ax=axs[0,1])
plot_histogram(df, 'fugitiveN2O_discharge', bins=25, ax=axs[1,0])
plot_histogram(df, 'fugitiveCH4_discharge', bins=25, ax=axs[1,1])
axs[0,0].axvspan(median_cis['processN2O_aerobic'].low, median_cis['processN2O_aerobic'].high, color=sns.color_palette()[1], label='95% CI Median')
axs[0,1].axvspan(median_cis['processCH4_aerobic'].low, median_cis['processCH4_aerobic'].high, color=sns.color_palette()[1], label='95% CI Median')
axs[1,0].axvspan(median_cis['fugitiveN2O_discharge'].low, median_cis['fugitiveN2O_discharge'].high, color=sns.color_palette()[1], label='95% CI Median')
axs[1,1].axvspan(median_cis['fugitiveCH4_discharge'].low, median_cis['fugitiveCH4_discharge'].high, color=sns.color_palette()[1], label='95% CI Median')
axs[0,0].axvline(nominal_vals['processN2O_aerobic'], color=sns.color_palette()[2], label='Nominal Value')
axs[0,1].axvline(nominal_vals['processCH4_aerobic'], color=sns.color_palette()[2], label='Nominal Value')
axs[1,0].axvline(nominal_vals['fugitiveN2O_discharge'], color=sns.color_palette()[2], label='Nominal Value')
axs[1,1].axvline(nominal_vals['fugitiveCH4_discharge'], color=sns.color_palette()[2], label='Nominal Value')
axs[0,0].set_xlabel('Process N$_2$O (Aerobic) [tCO$_2$eq/year]')
axs[0,1].set_xlabel('Process CH$_4$ (Aerobic) [tCO$_2$eq/year]')
axs[1,0].set_xlabel('Fugitive N$_2$O (Discharge) [tCO$_2$eq/year]')
axs[1,1].set_xlabel('Fugitive CH$_4$ (Discharge) [tCO$_2$eq/year]')
for ax in axs.flat:
	ax.legend()
fig.tight_layout()
plt.savefig('EmissionDistributions.png', dpi=300)

fig, ax = plt.subplots()
df_long = df.melt(value_vars=['processN2O_aerobic', 'processCH4_aerobic', 'fugitiveN2O_discharge', 'fugitiveCH4_discharge'])
sns.boxplot(df_long, x='variable', y='value')
ax.set_xticks([0,1,2,3], ['Process N$_2$O\n(Aerobic)', 'Process CH$_4$\n(Aerobic)', 'Fugitive N$_2$O\n(Discharge)', 'Fugitive CH$_4$\n(Discharge)'])
ax.set_xlabel(None)
ax.set_ylabel(r'Emissions [tCO$_2$eq/year]')
fig.tight_layout()
plt.savefig('EmissionBoxPlot.png', dpi=300)

fig, ax = plt.subplots()
plot_histogram(df, 'totalN2O', y='totalCH4', legend=True, ax=ax)
ax.set_xlabel('Total N$_2$O Emissions [tCO$_2$eq/year]')
ax.set_ylabel('Total CH$_4$ Emissions [tCO$_2$eq/year]')
plt.savefig('EmissionsTotalsDistributions.png', dpi=300)

fig, ax = plt.subplots()
plot_histogram(df, 'total', ax=ax)
plt.show()