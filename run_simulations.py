
import xlwings as xw
import pandas as pd

# Get the cell locations to modify
df = pd.read_excel('ParametersDistributions.xlsx', index_col=0)
cell_locs = df['cellLocation'].tolist()

# Open Excel
with xw.App() as app:
	# Get the workbook and sheets
	wb = app.books.open('Inventory.xlsm')
	input_sheet = wb.sheets('Inputs')
	summary_sheet = wb.sheets('Summary')

	# Run the simulations
	df = pd.read_excel('RandomSamples.xlsx', index_col=0)
	for idx, row in df.iterrows():
		print('Simulation {} of {}\r'.format(idx, len(df)), end="")
		
		# Change the input cells
		for i, val in row.items():
			cell = cell_locs[int(i)]
			input_sheet[cell_locs[int(i)]].value = val
		
		# Read the outputs
		df.loc[idx, 'processN2O_aerobic'] = summary_sheet['E6'].value
		df.loc[idx, 'processCH4_aerobic'] = summary_sheet['E7'].value
		df.loc[idx, 'fugitiveN2O_discharge'] = summary_sheet['E8'].value
		df.loc[idx, 'fugitiveCH4_discharge'] = summary_sheet['E10'].value

df.to_excel('SimulationResults.xlsx')