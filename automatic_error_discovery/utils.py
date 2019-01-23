from scipy.stats import norm
import pickle
import matplotlib.pyplot as plt
import glob
from random import shuffle
import copy
import math
import numpy as np
import json
from sklearn.metrics import precision_recall_fscore_support
from sklearn.metrics import accuracy_score
from scipy.stats import multivariate_normal
import csv as CSV

def dump_csv_data(base_folder="results_exp", binary=False, exp_type="advanced"):
	b_name = "binary" if binary==True else "multi"
	csv = []

	for i,filepath in enumerate(glob.iglob("{}/{}".format("{}/{}/{}".format(base_folder, b_name, exp_type), "/*.json"))):
		with open(filepath) as f:
			info = json.load(f)
		if i == 0:
			header = ["Dialogue History", "Acts", "Belief", "Entity", "BoW", "DB Consistency", "Confidence"]
			for k in info.keys():
				if "recall" in info[k].keys():
					for m in info["random"].keys():
						header.append("{}_{}".format(k.upper(), m))

			header.append("Best Model")
			header.append("Best F1")
			csv.append(header)

		row = []
		dial_histo = int(info['features']['Context window'])
		act = True if "prev" in info['features']['slice_vec'] else False
		belief = True if "slot" in info['features']['slice_vec'] else False
		entity = True if "entity" in info['features']['slice_vec'] else False
		BoW = info['features']['BoW']
		DB_Consistency = info['features']['Entity DB check']
		Confidence = "act + entity" if info['features']['Confidence featurization'] == "all" else info['features']['Confidence featurization']
		
		row.append(dial_histo)
		row.append(act)
		row.append(belief)
		row.append(entity)
		row.append(BoW)
		row.append(DB_Consistency)
		row.append(Confidence)

		for k in info.keys():
			if "recall" in info[k].keys():
				for m in info[k].keys():
					row.append(float(info[k][m]))
		row.append(info['best']['models'][-1].upper())
		row.append(float(info['best']['f1']))
		csv.append(row)

	csvfile = "{}/{}/{}/csv/csv_data.csv".format(base_folder, b_name, exp_type)
	with open(csvfile, "w") as output:
		writer = CSV.writer(output, lineterminator='\n')
		writer.writerows(csv)






def automatic_tuning(sklearn_classifier, param_grid, X):
	from sklearn.model_selection import GridSearchCV
	
	grid_search = GridSearchCV(sklearn_classifier.clf, param_grid, cv=5, scoring="f1_macro")
	x,y = sklearn_classifier.dump_train(X)
	grid_search.fit(x,y)
	print("== FineTuned model: {}".format(type(sklearn_classifier).__name__))
	print("== Params found: {}".format(json.dumps(grid_search.best_params_, indent=2)))
	sklearn_classifier.clf = grid_search.best_estimator_






def _add_turn(interaction):
	interaction['turns'] = []
	prev_index_turn = 0
	turn_steps = []

	for i,st in enumerate(interaction['steps']):
		if st['number'] > prev_index_turn or i == len(interaction['steps'])-1:
			_turn = copy.deepcopy(turn_steps)
			interaction['turns'].append(_turn)
			turn_steps = []
			prev_index_turn += 1

		turn_steps.append(st)


def add_turns(data_folder="/home/doomdiskday/Desktop/experiments/automatic_error_discovery/error_analysis_data", add=True):
	import numpy as np

	interactions = {}
	tot_turns = []
	tot_turns_BL = []

	for filepath in glob.iglob("{}/{}".format(data_folder, "/*.json")):
		with open(filepath, "rb") as f:
			interaction = pickle.load(f)
		int_id = interaction['user_id']
		if add == True:
			_add_turn(interaction)
		interactions[int_id] = interaction

	return interactions

def binarize_turn(x):
	for step in x:
		if step['error'] != "none":
			step['error'] = "error"
	return x

def load_data(data_folder="/home/doomdiskday/Desktop/experiments/automatic_error_discovery/error_analysis_data" ):
	interactions = {}
	for filepath in glob.iglob("{}/{}".format(data_folder, "/*.json")):
		with open(filepath, "rb") as f:
			interaction = pickle.load(f)
		int_id = interaction['user_id']
		interactions[int_id] = interaction

	return interactions

