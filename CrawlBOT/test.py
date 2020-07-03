def GetScore(text):
	# Save Model Using Pickle
	import pandas
	from sklearn import model_selection
	from sklearn.linear_model import LogisticRegression
	import pickle
	import numpy as np
	# load the model from disk


	loaded_model = pickle.load(open('engine.sav', 'rb'))
	print(loaded_model)
	return loaded_model.score([text],['EnTopico'])

print(GetScore('no hagamos nada'))