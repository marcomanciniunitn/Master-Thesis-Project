from sklearn.metrics import precision_recall_fscore_support
from sklearn.metrics import accuracy_score
from scipy.stats import multivariate_normal
from scipy.stats import norm
import pickle
import numpy as np
from SL_models import ErrorClassifier
import copy

class OneClassSVMTurn(ErrorClassifier):
	
	def __init__(self, threshold_classifier, nu=0.1, gamma=3, turn_context_window=1, step_context_window=1,
		prev_turn_context = 0, kernel="rbf", degree=3, 
		 BoW =None,  
		input_feature_map=None, slice_vec=["entity"], 
		labels={"none": 0, "dm": 1, "nlu": 2,  "both": 3}, 
		one_hot={"none": [1,0,0,0], "dm": [0,1,0,0], "nlu": [0,0,1,0], "both": [0,0,0,1]}):

		#best for context = 1: nu:0.35, gamma=4 [0.4912]
		#best for context = 3, nu:0.2, gamma=3 [0.52]
		#best for context = 4; nu=0.3, gamma = 3 [0.4982]

		from sklearn import svm
		self.clf = svm.OneClassSVM(nu=nu, kernel=kernel, gamma=gamma, degree=degree)
		self.threshold_classifier = threshold_classifier
		self.turn_context = turn_context_window
		self.step_context_window = step_context_window

		super(OneClassSVMTurn, self).__init__( BoW =BoW,  prev_turn_context = prev_turn_context,input_feature_map=input_feature_map, slice_vec=slice_vec,labels=labels, one_hot=one_hot)

	def normalize_steps(self, turn):
		new_turn = copy.deepcopy(turn)
		del new_turn['samples']
		new_turn['samples'] = []
		for i,st in enumerate(turn['samples'][0]):
			new_turn['samples'].append(np.delete(st,37))
		

		return new_turn
			

	def combine_steps(self, turn):
		turn = self.normalize_steps(turn)
		res = np.zeros(len((turn['samples'][-1]).flatten()))

		for st in turn['samples']:
			np.logical_or(st.flatten(), res, res)
			
		return self.slice_values(res.flatten()), turn['number']

	def featurize_turn(self, turn):
		new_turn, turn_number = self.combine_steps(turn)
		return np.array(new_turn).flatten(), turn_number

	def combine_steps_pred(self, turn):
		
		res = np.zeros(len((turn[0]['feat_vec_notflattened'][-1][-1]).flatten()))
		ind_acts = []

		for st in turn:
			np.logical_or(st['feat_vec_notflattened'][-1][-1].flatten(), res, res)

		return self.slice_values(res.flatten()), turn[0]['number']



	def featurize_turn_pred(self, turn):
		new_turn, turn_number = self.combine_steps_pred(turn)
		return np.array(new_turn).flatten(), turn_number
 


	def fit(self, X):
		contextualized_turns = []

		for turn in X:
			t, turn_number = self.featurize_turn(turn)
			t2 = self.contextualize_turn(t, turn_number)
			contextualized_turns.append(t2)

		self.clf.fit(contextualized_turns)

	def dump_train(self, X):
		contextualized_turns = []
		y = []

		for turn in X:
			t, turn_number = self.featurize_turn(turn)
			t2 = self.contextualize_turn(t, turn_number)
			contextualized_turns.append(t2)
			y.append(1)

		return contextualized_turns, y 

	def predict(self,x):
		x_feats, turn = self.featurize_turn_pred(x)
		x_feats = self.contextualize_turn(x_feats, turn)

		
		pred = self.clf.predict([x_feats])[0]


		if (pred == 1):
			return self.labels['none']
		else:
			return self.threshold_classifier.predict(x)

	def dump_grid_search_data(self, X, dev):
		contextualized_turns = []
		y = []

		for turn in X:
			t, turn_number = self.featurize_turn(turn)
			t2 = self.contextualize_turn(t, turn_number)
			contextualized_turns.append(t2)
			y.append(1)

		for x in dev:
			x_feats, turn = self.featurize_turn_pred(x)
			x_feats = self.contextualize_turn(x_feats, turn)

			contextualized_turns.append(x_feats)
			y.append(self.labels[x[0]['error']])
		import random
		tot = list(zip(contextualized_turns, y))
		random.shuffle(tot)
		contextualized_turns, y = zip(*tot)
		return contextualized_turns, y

	def dump(self, folder="models/ONE_CLASS/"):
		with open("{}{}".format(folder, "SVMTurn"), "wb+") as f:
			pickle.dump(self.__dict__,f)

	def load(self, folder="models/ONE_CLASS/"):       
		with open("{}{}".format(folder, "SVMTurn"), "rb") as f:
			self.__dict__.update(pickle.load(f))




class BinaryOneClassSVMTurn(OneClassSVMTurn):
	
	def __init__(self, threshold_classifier, nu=0.1, gamma=3, turn_context_window=1, step_context_window=1,
		prev_turn_context = 0, kernel="rbf", degree=3, 
		 BoW =None,  
		input_feature_map=None, slice_vec=["entity"], 
		labels={"none": 0, "error": 1}, 
		one_hot={"none": [0], "error": [1]}):

		#best for context = 1: nu:0.35, gamma=4 [0.4912]
		#best for context = 3, nu:0.2, gamma=3 [0.52]
		#best for context = 4; nu=0.3, gamma = 3 [0.4982]

		from sklearn import svm
		super(BinaryOneClassSVMTurn, self).__init__( BoW = BoW,  threshold_classifier=threshold_classifier, nu=nu, gamma=gamma,
													turn_context_window=turn_context_window, step_context_window=step_context_window,
													prev_turn_context = prev_turn_context,
													input_feature_map=input_feature_map, slice_vec=slice_vec,
													labels=labels, one_hot=one_hot)

	def predict(self,x):
		x_feats, turn = self.featurize_turn_pred(x)
		x_feats = self.contextualize_turn(x_feats, turn)

		
		pred = self.clf.predict([x_feats])[0]
		print(pred)

		return self.labels['none'] if pred == 1 else self.labels['error']

	def dump(self, folder="models/ONE_CLASS/"):
		with open("{}{}".format(folder, "binarySVMTurn"), "wb+") as f:
			pickle.dump(self.__dict__,f)

	def load(self, folder="models/ONE_CLASS/"):       
		with open("{}{}".format(folder, "binarySVMTurn"), "rb") as f:
			self.__dict__.update(pickle.load(f))


class IsolationForestTurn(ErrorClassifier):
	
	def __init__(self, threshold_classifier, n_estimators=100, max_features=1.0, n_jobs=4, context_window=1,
		prev_turn_context = 0,
		 BoW =None,  
		input_feature_map=None, slice_vec=["entity"], 
		labels={"none": 0, "dm": 1, "nlu": 2,  "both": 3}, 
		one_hot={"none": [1,0,0,0], "dm": [0,1,0,0], "nlu": [0,0,1,0], "both": [0,0,0,1]}):


		from sklearn.ensemble import IsolationForest
		self.clf = IsolationForest(n_estimators=n_estimators, max_features=float(max_features), n_jobs=n_jobs)
		self.threshold_classifier = threshold_classifier
		self.context = context_window

		super(IsolationForestTurn, self).__init__( BoW =BoW,  prev_turn_context = prev_turn_context,input_feature_map=input_feature_map, slice_vec=slice_vec,labels=labels, one_hot=one_hot)

	
	def normalize_steps(self, turn):
		new_turn = copy.deepcopy(turn)
		del new_turn['samples']
		new_turn['samples'] = []
		for i,st in enumerate(turn['samples'][0]):
			new_turn['samples'].append(np.delete(st,37))
		

		return new_turn
			

	def combine_steps(self, turn):
		turn = self.normalize_steps(turn)
		res = np.zeros(len((turn['samples'][-1]).flatten()))

		for st in turn['samples']:
			np.logical_or(st.flatten(), res, res)
			

		return self.slice_values(res.flatten()), turn['number']

	def featurize_turn(self, turn):
		new_turn, turn_number = self.combine_steps(turn)
		return np.array(new_turn).flatten(), turn_number

	def combine_steps_pred(self, turn):
		
		res = np.zeros(len((turn[0]['feat_vec_notflattened'][-1][-1]).flatten()))
		ind_acts = []

		for st in turn:
			np.logical_or(st['feat_vec_notflattened'][-1][-1].flatten(), res, res)

		return self.slice_values(res.flatten()), turn[0]['number']



	def featurize_turn_pred(self, turn):
		new_turn, turn_number = self.combine_steps_pred(turn)
		return np.array(new_turn).flatten(), turn_number
 


	def fit(self, X):
		contextualized_turns = []

		for turn in X:
			t, turn_number = self.featurize_turn(turn)
			t2 = self.contextualize_turn(t, turn_number)
			contextualized_turns.append(t2)

		self.clf.fit(contextualized_turns)

	def dump_train(self, X):
		contextualized_turns = []
		y = []

		for turn in X:
			t, turn_number = self.featurize_turn(turn)
			t2 = self.contextualize_turn(t, turn_number)
			contextualized_turns.append(t2)
			y.append(1)

		return contextualized_turns, y 

	def predict(self,x):
		x_feats, turn = self.featurize_turn_pred(x)
		x_feats = self.contextualize_turn(x_feats, turn)

		
		pred = self.clf.predict([x_feats])[0]


		if (pred == 1):
			return self.labels['none']
		else:
			return self.threshold_classifier.predict(x)

	def dump_grid_search_data(self, X, dev):
		contextualized_turns = []
		y = []

		for turn in X:
			t, turn_number = self.featurize_turn(turn)
			t2 = self.contextualize_turn(t, turn_number)
			contextualized_turns.append(t2)
			y.append(1)

		for x in dev:
			x_feats, turn = self.featurize_turn_pred(x)
			x_feats = self.contextualize_turn(x_feats, turn)

			contextualized_turns.append(x_feats)
			y.append(self.labels[x[0]['error']])
		import random
		tot = list(zip(contextualized_turns, y))
		random.shuffle(tot)
		contextualized_turns, y = zip(*tot)
		return contextualized_turns, y

	def dump(self, folder="models/ONE_CLASS/"):
		with open("{}{}".format(folder, "ISOLATION_step"), "wb+") as f:
			pickle.dump(self.__dict__,f)

	def load(self, folder="models/ONE_CLASS/"):       
		with open("{}{}".format(folder, "ISOLATION_step"), "rb") as f:
			self.__dict__.update(pickle.load(f))



class BinaryIsolationForestTurn(IsolationForestTurn):
	
	def __init__(self, threshold_classifier, n_estimators=100, max_features=1.0, n_jobs=4, context_window=1,
		prev_turn_context = 0,
		 BoW =None,  
		input_feature_map=None, slice_vec=["entity"], 
		labels={"none": 0, "error": 1}, 
		one_hot={"none": [0], "error": [1]}):


		from sklearn import svm
		super(BinaryIsolationForestTurn, self).__init__( BoW =BoW,  threshold_classifier=threshold_classifier,
														n_estimators=n_estimators, max_features=max_features, n_jobs=n_jobs,
														context_window=context_window,
														prev_turn_context = prev_turn_context,
														input_feature_map=input_feature_map, slice_vec=slice_vec,
														labels=labels, one_hot=one_hot)
	def predict(self,x):
			x_feats, turn = self.featurize_turn_pred(x)
			x_feats = self.contextualize_turn(x_feats, turn)
			
			pred = self.clf.predict([x_feats])[0]

			return self.labels['none'] if pred == 1 else self.labels['error']

	def dump(self, folder="models/ONE_CLASS/"):
		with open("{}{}".format(folder, "binaryIsolationForestTurn"), "wb+") as f:
			pickle.dump(self.__dict__,f)

	def load(self, folder="models/ONE_CLASS/"):       
		with open("{}{}".format(folder, "binaryIsolationForestTurn"), "rb") as f:
			self.__dict__.update(pickle.load(f))
