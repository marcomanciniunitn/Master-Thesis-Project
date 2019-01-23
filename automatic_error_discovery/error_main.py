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
from sklearn.metrics import f1_score
from sklearn.metrics import accuracy_score
from scipy.stats import multivariate_normal

from SL_models import *
from ND_models import *
from utils import *

from tqdm import tqdm 
import inspect
import os 

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

np.warnings.filterwarnings('ignore')


def retrieve_data_for_gaussians(data="restaurant_server/data/error_analysis_data.pck"):
	with open(data, "rb") as f:
		data = pickle.load(f)
	return data['entities'], data['actions']

def retrieve_data_for_ONECLASS(data="restaurant_server/data/one_class_data.pck"):
	with open(data, "rb") as f:
		data = pickle.load(f)

	return data

def print_error_summary(turn):
	print("=> Error type: {}".format(turn[0]['error']))
	print("=> User Said: {}".format(turn[0]['text']))
	print("=> Turn Number: {}".format(turn[0]['number']))
	print("+ ENTITIES +")
	for ent in turn[0]['entities']:
		print("=> Entity Name: {} - Entity Value: {} - Confidence: {}".format(ent['entity'], ent['value'], ent['confidence']))
	print("+ ACTS +")
	for st in turn:
		print("=> Action: {} - Confidence: {}".format(st['act']['act'], st['act']['confidence']))
	

def check_errors(data_folder="/home/doomdiskday/Desktop/experiments/automatic_error_discovery/error_analysis_data", exp_type="baseline", error="nlu", binary=False):
	interactions = add_turns(data_folder)

	for i in interactions.keys():
		if interactions[i]['exp_type'] == exp_type:
			interactions[i]['turns'] = [x if binary == False else binarize_turn(x) for x in interactions[i]['turns'] if x[0]['error'] != "after" and x[0]['error'] != "dontknow"]

			for j,turn in enumerate(interactions[i]['turns']):
				if turn[0]['error'] != "none":
					print("\n\n---------------------------------------------")
					print("===== ERROR FOUND! =====")
					print_error_summary(turn)
					
					if j != 0:
						print("\n== PREVIOUS TURN ==")
						print_error_summary(interactions[i]['turns'][j-1])
					print("---------------------------------------------")

def retag_dataset(data_folder="/home/doomdiskday/Desktop/experiments/automatic_error_discovery/error_analysis_data", exp_type="baseline", n_good=3, binary=False):
	interactions = add_turns(data_folder)
	new_interactions = {}
	good_interacions = {}

	found_err = False
	for i in interactions.keys():
		if interactions[i]['exp_type'] == exp_type:
			interactions[i]['turns'] = [x if binary == False else binarize_turn(x) for x in interactions[i]['turns'] if x[0]['error'] != "after" and x[0]['error'] != "dontknow"]

			for j,turn in enumerate(interactions[i]['turns']):
				if turn[0]['error'] != "none":
					found_err = True
					print("\n\n---------------------------------------------")
					print("===== ERROR FOUND! =====")
					print_error_summary(turn)
					
					if j != 0:
						print("\n== PREVIOUS TURN ==")
						print_error_summary(interactions[i]['turns'][j-1])
					print("---------------------------------------------")
					new_error = input("Enter new error type:")
					new_turn = input("Enter the turn number:")
					new_turn = int(new_turn)
					new_interactions[i] = copy.deepcopy(interactions[i])
					print("ERROR_ID : {}".format(i))

					for k,i_turn in enumerate(new_interactions[i]['turns']):
						if k == new_turn:
						#if turn[0]['error'] != "none":
							for l,st in enumerate(i_turn):

								new_interactions[i]['turns'][k][l]['error'] = new_error
						if k > new_turn:
							for l,st in enumerate(i_turn):

								new_interactions[i]['turns'][k][l]['error'] = "none"
						

					with open("/home/doomdiskday/Desktop/experiments/automatic_error_discovery/error_analysis_data/retagged_adv/" + i + ".json", "wb") as f:
						pickle.dump(new_interactions[i], f)


	for i in interactions.keys():
		if interactions[i]['exp_type'] == exp_type and i not in new_interactions.keys() and n_good > 0:
			good_interacions[i] = copy.deepcopy(interactions[i])
			n_good -= 1

	for l in good_interacions.keys():
		with open("/home/doomdiskday/Desktop/experiments/automatic_error_discovery/error_analysis_data/retagged_adv/" + l + ".json", "wb") as f:
			pickle.dump(good_interacions[l], f)

def calculate_overlap(retagged_data_folder="/home/doomdiskday/Desktop/experiments/automatic_error_discovery/error_analysis_data/retagged_adv/",
 					  original_data_folder="/home/doomdiskday/Desktop/experiments/automatic_error_discovery/error_analysis_data/",
 					  exp_type="baseline", binary=False):
	from sklearn.metrics import cohen_kappa_score
	retagged_interactions = add_turns(retagged_data_folder, add=False)
	original_interactions = add_turns(original_data_folder, add=True)

	if binary == False:
		overlaps = {"nlu": [0,0],
				  "dm": [0,0],
				  "both": [0,0],
				  "none": [0,0]}
		labels = {"none": 0, "dm": 1, "nlu": 2, "both": 3}
	else:
		overlaps = {"none": [0,0],
		  "error": [0,0]}
		labels = {"none": 0, "error": 1}

	tester_labels = []
	true_labels = []
	for i in retagged_interactions.keys():
		if retagged_interactions[i]['exp_type'] == exp_type:
			retagged_interactions[i]['turns'] = [x if binary == False else binarize_turn(x) for x in retagged_interactions[i]['turns'] if x[0]['error'] != "after" and x[0]['error'] != "dontknow"]
			original_interactions[i]['turns']= [x if binary == False else binarize_turn(x) for x in original_interactions[i]['turns'] if x[0]['error'] != "after" and x[0]['error'] != "dontknow"]

			for j,(re_turn, or_turn) in enumerate(zip(retagged_interactions[i]['turns'], original_interactions[i]['turns'])):
				true_error = re_turn[0]['error']

				true_labels.append(labels[re_turn[0]['error']])


				orig_error = or_turn[0]['error']


				tester_labels.append(labels[or_turn[0]['error']])

				overlaps[true_error][0] += 1
				if true_error == orig_error:
					overlaps[orig_error][1] += 1 

	print("===== OVERLAP STATISTICS =====")
	tot_overlap = 0
	for k,v in overlaps.items():
		print("+ ERROR: {} - Overlap: {}/{} [{}%]".format(k, v[1], v[0], float(v[1]/v[0]) if v[0] > 0 else 0))
		tot_overlap += float(v[1]/v[0]) if v[0] > 0 else 0
	print("yee")
	print(len(true_labels))
	print("AVERAGE TOTAL OVERLAP: {}%".format(tot_overlap/len(overlaps)))
	print("Cohen Kappa Score: {}".format(cohen_kappa_score(tester_labels, true_labels)))
	pre, rec, f1, sup = precision_recall_fscore_support(true_labels, tester_labels, average="macro")
	print("F1-micro: {}".format(precision_recall_fscore_support(true_labels, tester_labels, average="micro")[2]))
	print("F1-macro: {}".format(precision_recall_fscore_support(true_labels, tester_labels, average="macro")[2]))
	print("Precision: {}".format(pre))
	print("Recall: {}".format(rec))
				


def generate_threshold_data(data_folder="/home/doomdiskday/Desktop/experiments/automatic_error_discovery/error_analysis_data", exp_type="baseline"):
	interactions = add_turns(data_folder)
	NLU_confidences = []
	DM_confidences = []
	for i in interactions.keys():
		for turn in interactions[i]['turns']:
			NLU_confidences.extend([float(ent['confidence']) for ent in turn[0]['entities']])
			for st in turn:
				DM_confidences.append(float(st['act']['confidence']))
	return NLU_confidences, DM_confidences

def generate_K_folds(data_folder="/home/doomdiskday/Desktop/experiments/automatic_error_discovery/error_analysis_data", exp_type="advanced", binary=False):
	interactions = add_turns(data_folder)

	folds = []
	fold = {"training_dialogues": [], "test_dialogues":[], "training_stats": {}, "test_stats": {}}
	if binary == False:
		Y_counters = {"nlu": 0,
				  "dm": 0,
				  "both": 0,
				  "none": 0}
	else:
		Y_counters = {"none": 0,
		  "error": 0}

	for i in interactions.keys():
		if interactions[i]['exp_type'] == exp_type:
			interactions[i]['turns'] = [x if binary == False else binarize_turn(x) for x in interactions[i]['turns'] if x[0]['error'] != "after" and x[0]['error'] != "dontknow"]
			_fold = copy.deepcopy(fold)
			_fold['test_dialogues'] = [x for x in interactions[i]['turns'] if interactions[i]['exp_type'] == exp_type]

			for j in interactions.keys():
				interactions[j]['turns'] = [x if binary == False else binarize_turn(x) for x in interactions[j]['turns'] if x[0]['error'] != "after" and x[0]['error'] != "dontknow"]
				if j != i:
					_fold['training_dialogues'].extend([x for x in interactions[j]['turns'] if interactions[j]['exp_type'] == exp_type])

			_tr_stats = copy.deepcopy(Y_counters)
			_fold['training_stats'] = copy.deepcopy(Y_counters)
			_fold['test_stats'] = copy.deepcopy(Y_counters)

			for trn in _fold['training_dialogues']:
				_fold['training_stats'][trn[0]['error']] += 1

			for trn in _fold['test_dialogues']:
				_fold['test_stats'][trn[0]['error']] += 1
			folds.append(_fold)

	return folds

def filter_folds(folds):
	new_folds = []
	filtered = 0
	for fold in folds:
		error_counter = 0
		for k,v in fold['test_stats'].items():
			if k != "none":
				if v != 0:
					error_counter += 1
		if error_counter != 0:
			new_folds.append(fold)
		else:
			filtered += 1

	return new_folds, filtered

def run_tests(exp_type="advanced", binary=False):
	slice_vec_empty = ["intent"]
	slice_vec_ent = ["entity"]
	slice_vec_belief = ["slot"]
	slice_vec_act = ["prev"]
	slice_vec_ent_belief = ["entity", "slot"]
	slice_vec_ent_act = ["entity", "prev"]
	slice_vec_belief_act = ["slot", "prev"]
	slice_vec_full = ["entity", "prev", "slot"]
	
	slice_vecs = [slice_vec_empty, slice_vec_ent, slice_vec_belief, slice_vec_act, slice_vec_ent_belief,slice_vec_ent_act, slice_vec_belief_act, slice_vec_full]
	vectorizer = [True, False]
	entity_check = [True, False]
	confidence = ["none", "act", "entity", "all"]
	context_windows = [0,1,2,3,4,5]
	
	prohibited = [["intent", False, False, "none"]]


	tqdm_cntx = tqdm(context_windows)
	tqdm_slicevec = tqdm(slice_vecs)
	tqdm_vectorizer = tqdm(vectorizer)
	tqdm_entities = tqdm(entity_check)
	tqdm_conf = tqdm(confidence)

	for c in tqdm_cntx:
		tqdm_cntx.set_description("Context: {}".format(c))
		for slice_v in tqdm_slicevec:
			
			tqdm_slicevec.set_description("Slice Vector: {}".format(slice_v))
		
			for vect in tqdm_vectorizer:
				tqdm_vectorizer.set_description("BoW: {}".format(vect))
				for ent in tqdm_entities:
					tqdm_entities.set_description("DB entity check: {}".format(ent))
					for conf in tqdm_conf:		
						tqdm_conf.set_description("Confidence feature: {}".format(conf))
						_conf = [slice_v[0], vect, ent, conf]
						if _conf not in prohibited:
							run_K_folds(exp_type=exp_type, slice_vec=slice_v, context=c, feature_confidence=conf, vectorizer=vect, entity_check=ent, binary=binary)
	

def find_best(exp_type="advanced", binary=True):
	best_f1 = 0.0
	best_model = None
	best_features = []
	file = None
	b_name = "binary" if binary == True else "multi"
	for filepath in glob.iglob("{}/{}".format("results_exp/{}/{}".format(b_name, exp_type), "/*.json")):
		with open(filepath, "r") as f:
			summary = json.load(f)
		if float(summary['best'] ['f1']) > best_f1:
			best_model = summary['best']['models'][-1]
			best_f1 = float(summary['best'] ['f1'])

			file = filepath
	
	print(best_f1)
	print(file)



def run_K_folds(exp_type="advanced", filter_noerrors=True, slice_vec = [], context = 0, 
	feature_confidence ="none", vectorizer=False, entity_check=False, binary=False):


	folds = generate_K_folds(exp_type=exp_type, binary=binary)
	
	with open("input_feature_map.pck", "rb") as f:
		input_feature_map = pickle.load(f)
		input_feature_map = normalize_input_map(input_feature_map)


	if binary == True:
		BINARY_labels={"none": 0, "error": 1} 
		BINARY_labels_forest={"none": 0, "error": -1} 
		BINARY_one_hot={"none": [0], "error": [1]}
		BINARY_one_hot_forest ={"none": [0], "error": [-1]}
		PROB_vect = [0.5, 0.5]
	else:
		BINARY_labels= {"none": 0, "dm": 1, "nlu": 2,  "both": 3}
		BINARY_labels_forest={"none": 0, "dm": -1, "nlu": -1, "both": - 1} 

		BINARY_one_hot={"none": [1,0,0,0], "dm": [0,1,0,0], "nlu": [0,0,1,0], "both": [0,0,0,1]}
		BINARY_one_hot_forest ={"none": [0], "error": [-1]}
		
		PROB_vect = [0.25, 0.25, 0.25, 0.25]




	slice_vec = slice_vec
	turn_context = context
	context_window = 0
	featurize_confidence = feature_confidence
	vectorizer = vectorizer
	entity_check = entity_check
	features = [slice_vec, turn_context, featurize_confidence, vectorizer, entity_check]

	from sklearn.linear_model import LogisticRegression
	logit_C=0.1
	logit_solver="liblinear"
	logit_clf = LogisticRegression(C=logit_C, solver=logit_solver, dual=True, class_weight="balanced", max_iter=50)

	from sklearn.svm import SVC
	svc_c = 0.001
	kernel_svc = "linear"
	degree_svc = 1
	gamma_svc = 0.0001
	svm_clf = SVC(C=svc_c, kernel=kernel_svc, gamma=gamma_svc, degree=degree_svc)


	from sklearn.ensemble import IsolationForest
	n_estimators=50
	max_features=0.7
	n_jobs=4
	contamination=0.001
	random_forest_clf = IsolationForest(n_estimators=n_estimators, max_features=float(max_features), n_jobs=n_jobs)


	from sklearn.neural_network import MLPClassifier
	hidden_layer_size = (10	, )
	max_iter = 80
	alpha=0.001 
	solver="lbfgs" #lbfgs suggested for small dataset, use "adam" instead
	activation="relu" 
	batch_size = "auto"
	learning_rate = "constant" 
	learning_rate_init = 0.001
	mlp_clf = MLPClassifier(hidden_layer_sizes= hidden_layer_size, max_iter=max_iter, alpha=alpha,
                    solver=solver, activation=activation, batch_size=batch_size, learning_rate=learning_rate, learning_rate_init=learning_rate_init)



	random_class = RandomClassifier(labels=BINARY_labels, one_hot=BINARY_one_hot, probabilities=PROB_vect, input_feature_map=input_feature_map, slice_vec=slice_vec)
	t_class = BinaryThresholdClassifier(T1=0.94, T2=0.65, input_feature_map=input_feature_map, slice_vec=slice_vec)
	#t_class.learn_thresholds(DM_confidences, NLU_confidences)
	maj_model = MajorityModel(labels=BINARY_labels, one_hot=BINARY_one_hot, input_feature_map=input_feature_map, slice_vec=slice_vec)

	logit = SKLearnClassifier(clf=logit_clf, featurize_confidence=featurize_confidence, entity_check=entity_check,
		input_feature_map=input_feature_map, labels=BINARY_labels,
		one_hot=BINARY_one_hot, slice_vec=slice_vec, prev_turn_context= turn_context, context_window=context_window,
		BoW=vectorizer)

	
	lin_SVC = SKLearnClassifier(clf=svm_clf, featurize_confidence= featurize_confidence, entity_check=entity_check,
		input_feature_map=input_feature_map, labels=BINARY_labels,
		one_hot=BINARY_one_hot, slice_vec=slice_vec, prev_turn_context= turn_context, context_window=context_window,
		BoW=vectorizer)

	random_forest = SKLearnClassifier(clf=random_forest_clf, featurize_confidence=featurize_confidence, entity_check=entity_check,
		input_feature_map=input_feature_map, labels=BINARY_labels_forest ,
		one_hot=BINARY_one_hot_forest, slice_vec=slice_vec, prev_turn_context= turn_context, context_window=context_window,
		BoW=vectorizer)

	mlp = SKLearnClassifier(clf=mlp_clf, featurize_confidence=featurize_confidence, entity_check=entity_check,
		input_feature_map=input_feature_map, labels=BINARY_labels,
		one_hot=BINARY_one_hot, slice_vec=slice_vec, prev_turn_context= turn_context, context_window=context_window,
		BoW=vectorizer)


	from auto_encoder import MyAutoEncoder
	neural_detector = MyAutoEncoder( input_feature_map=input_feature_map, featurize_confidence=featurize_confidence, entity_check=entity_check,
		labels=BINARY_labels,
		one_hot=BINARY_one_hot, slice_vec=slice_vec, prev_turn_context= turn_context,
		BoW=vectorizer)
	


	_models = ["random", "threshold", "majority", "LinearSVM", "Logit", "RandomForest", "MLP" , "Neural-Detector"]
	#_models = ["random", "threshold", "majority", "Logit"]
	_metrics = {"accuracy": 0, "precision": 0, "recall": 0, "f1": 0}

	summary_perf = {k: copy.deepcopy(_metrics) for k in _models}
	
	
	filtered = 0
	if filter_noerrors == True:
		folds, filtered= filter_folds(folds)

	tqdm_folds = tqdm(folds)
	for fold in tqdm_folds:
		tqdm_folds.set_description("Fold")
		
		t_class.learn_thresholds(fold['training_dialogues'])
		maj_model.fit(fold['training_dialogues'])

		__turns, __y_turns = lin_SVC.dump_train(fold['training_dialogues'])
		

		#Hypertuning SVM
		param_grid_SVC = {"C": [0.001, 0.01], "kernel": ["linear", "poly", "rbf"], "degree": [1,2], "gamma": [0.0001, 0.001]}
		automatic_tuning(lin_SVC, param_grid_SVC, fold['training_dialogues'])
		lin_SVC.fit_no_comp(__turns, __y_turns, fold['training_dialogues'])

		#Hypertuning logit
		param_grid_logit = {"C": [0.1, 1, 1e5, 1e7], "dual": [True, False], "class_weight": ["balanced"], "max_iter": [50, 100]}
		automatic_tuning(logit, param_grid_logit, fold['training_dialogues'])
		logit.fit_no_comp(__turns, __y_turns, fold['training_dialogues'])


		#Hypertuning isolation forest
		param_grid_iso = {"n_estimators": [50, 100], "max_samples": [0.7, 1.0], "contamination": [0.001, 0.01], "n_jobs": [4]}
		automatic_tuning(random_forest, param_grid_iso, fold['training_dialogues'])
		random_forest.fit_no_comp(__turns, __y_turns, fold['training_dialogues'])


		#Hypertuning MLP
		param_grid_MLP = {"hidden_layer_sizes": [(10,)],
						 "max_iter": [20, 50, 80], "alpha": [0.0001, 0.001],
						  "learning_rate": ["constant"]}
		automatic_tuning(mlp, param_grid_MLP, fold['training_dialogues'])
		mlp.fit_no_comp(__turns, __y_turns, fold['training_dialogues'])
		neural_detector.fit_no_comp(__turns, __y_turns, fold['training_dialogues'])

		if turn_context > 0:
			lin_SVC.reset_turn_memory()
			logit.reset_turn_memory()
			random_forest.reset_turn_memory()
			mlp.reset_turn_memory()
			neural_detector.reset_turn_memory()

		labels = random_class.labels
		predictions = {k : [] for k in _models}
		true_labels = [labels[x[0]['error']] for x in fold['test_dialogues']]
		for x in fold['test_dialogues']:
			r_pred = random_class.predict(x) 
			t_pred = t_class.predict(x)
			m_pred = maj_model.predict(x)
			l_pred = lin_SVC.predict(x)
			logit_pred = logit.predict(x)
			
			if binary == True:
				r_forest_pred = 0 if random_forest.predict(x) == 1 else 1
			else:
				r_forest_pred = t_class.predict(x) if r_pred == -1 else 1

			mlp_pred = mlp.predict(x)
			neural_pred = neural_detector.predict(x)[0]
			
			

			predictions['random'].append(r_pred)
			predictions['threshold'].append(t_pred)
			predictions['majority'].append(m_pred)
			predictions['LinearSVM'].append(l_pred)
			predictions['Logit'].append(logit_pred)
			
			predictions['RandomForest'].append(r_forest_pred)
			predictions['MLP'].append(mlp_pred)
			predictions['Neural-Detector'].append(neural_pred)
			
		
		summaries = summary_errors(predictions, true_labels, labels)

		for i,mod in enumerate(predictions.keys()):
				acc = accuracy_score(true_labels, predictions[mod])
				pre, rec, f1, sup = precision_recall_fscore_support(true_labels, predictions[mod], average='macro')

				summary_perf[mod]['accuracy'] += (acc)
				summary_perf[mod]['precision'] += (pre)
				summary_perf[mod]['recall'] += (rec)
				summary_perf[mod]['f1'] += (f1)
				
	#closing DB connections.
	random_class.closeDB()
	t_class.closeDB()
	maj_model.closeDB()
	lin_SVC.closeDB()
	logit.closeDB()
	random_forest.closeDB()
	mlp.closeDB()
	neural_detector.closeDB()

	for k in summary_perf.keys():
		for kk, v in summary_perf[k].items():
			summary_perf[k][kk] = str(float(v / len(folds)))

	name_dump = "CONTEXT:" + str(turn_context) + "_SLICEVEC:"
	for s in slice_vec:
		name_dump += "+" + s 
	name_dump += "_"

	name_dump += "CONFIDENCE:" + featurize_confidence + "_" 
	name_dump += "BOW:true_" if vectorizer == True else "BOW:false_"
	name_dump += "ENTITYCHECK:true" if entity_check == True else "ENTITYCHECK:false"
	best_model = []
	best_f1 = 0.0
	for mod in summary_perf.keys():
		if float(summary_perf[mod]["f1"]) >= best_f1:
			best_model.append(mod)
			best_f1 = float(summary_perf[mod]["f1"])

	summary_perf['best'] = {"models": best_model, "f1": best_f1}

	summary_perf["features"] = {"slice_vec": slice_vec, "Confidence featurization": featurize_confidence, 
								"BoW": vectorizer, "Entity DB check": entity_check, "Context window": str(turn_context)}
	b_name = "binary" if binary == True else "multi"
	with open("results_exp/{}/{}/{}.json".format(b_name, exp_type, name_dump) , "w+") as f:
		json.dump(summary_perf, f, indent=2)
	
	del random_class
	del t_class
	del maj_model
	del lin_SVC
	del logit
	del random_forest
	del mlp
	del neural_detector	

def generate_test_dev_sets(data_folder="/home/doomdiskday/Desktop/experiments/automatic_error_discovery/error_analysis_data",
						  dev_split=0.60, exp_type="baseline", binary=False, add_turn=True):

	interactions = add_turns(data_folder, add=add_turn)
	
	tot_turns = []
	tot_turns_BL = []

	if binary == False:
		Y_counters = {"nlu": 0,
				  "dm": 0,
				  "both": 0,
				  "none": 0}
	else:
		Y_counters = {"none": 0,
		  "error": 0}


	#Accumulate steps and counters for test and dev set splits
	for i in interactions.keys():

		interactions[i]['turns'] = [x if binary == False else binarize_turn(x) for x in interactions[i]['turns'] if x[0]['error'] != "after" and x[0]['error'] != "dontknow"]
		

		to_check_and_add = [x for x in interactions[i]['turns'] if interactions[i]['exp_type'] == exp_type]
		tot_turns += to_check_and_add


		for trn in to_check_and_add:
			Y_counters[trn[0]['error']] += 1 

	#Start generating development and test set keeping Y label distribution
	dev_set = []
	dev_splits = {k: int(round((Y_counters[k] * dev_split))) for k in Y_counters.keys()}
	
	for d in dev_splits.keys():
		if dev_splits[d] == 0 and Y_counters[d] != 0:
			dev_splits[d] = 1

	for err_type in dev_splits.keys():
		to_del_indexes = []
		for k,t in enumerate(tot_turns):
			if dev_splits[err_type] < 1:
				break
			if t[0]['error'] == err_type:
				
				_tcpy = copy.deepcopy(t)
				dev_set.append(_tcpy)
				to_del_indexes.append(k)
				dev_splits[err_type] -= 1

		tot_turns = [i for j, i in enumerate(tot_turns) if j not in to_del_indexes]	
	
	_teststats = {k:0 for k in Y_counters.keys()}
	_devstats = copy.deepcopy(_teststats)

	for x in tot_turns:
		_teststats[x[0]['error']] += 1
	for x in dev_set:
		_devstats[x[0]['error']] += 1

	
	print("-- Dataset information")
	for err_t, samples in Y_counters.items():
		print(" ERROR: {}   [SAMPLES: {}]".format(err_t, samples))
	
	
	return tot_turns, dev_set, _teststats, _devstats

def summary_errors(pred, true, labels):
	class_summ = {"correct": 0,
				   "others": 0,
				   "N_true": 0}

	algo_sum = {"name": None,
				"predict_summary": {}}

	summaries = []
	inv_labels = {v:k for k,v in labels.items()}

	for p in pred.keys():
		_algo_sum = copy.deepcopy(algo_sum)
		_algo_sum['name'] = p
		for k in labels.keys():
			_class_sum = copy.deepcopy(class_summ)
			_algo_sum['predict_summary'][k] = _class_sum
		for i,pred_val in enumerate(pred[p]):

			pred_label = inv_labels[pred_val]
			true_label = inv_labels[true[i]]
			if pred_val == true[i]:
				_algo_sum['predict_summary'][pred_label]['correct'] += 1
			else:
				_algo_sum['predict_summary'][true_label]['others'] += 1
			_algo_sum['predict_summary'][true_label]['N_true'] += 1
		summaries.append(_algo_sum)

	return summaries


def normalize_input_map(input_feature_map):
	kk = 0
	to_ret = {}
	for k,v in input_feature_map.items():
		if k != "slot_text_0":
			input_feature_map[k] = kk
			to_ret[k] = kk
			kk +=1

	return to_ret

def calculate_BOW(dev_set):
	from sklearn.feature_extraction.text import CountVectorizer

	sentences = []
	for turn in dev_set:
		sentences.append(turn[0]['text'])

	vectorizer = CountVectorizer()
	vectorizer.fit(sentences)
	return vectorizer


	

run_tests(exp_type="advanced", binary=True)
dump_csv_data(base_folder="results_exp", binary=True, exp_type="advanced")

