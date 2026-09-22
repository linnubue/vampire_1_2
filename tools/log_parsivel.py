import yaml
import pyAtmosLogger.instruments.ottParsivel2VAMPIRE as instrumentClass

with open(r'C:\users\mirac\Documents\vampire\instrument.yaml','r') as file:
	config = yaml.safe_load(file)

instrument = instrumentClass.ottParsivel2VAMPIRE(config)

instrument.log()
