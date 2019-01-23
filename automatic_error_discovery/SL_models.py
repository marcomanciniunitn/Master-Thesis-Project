from sklearn.metrics import precision_recall_fscore_support
from sklearn.metrics import accuracy_score
from scipy.stats import multivariate_normal
from scipy.stats import norm
import pickle
import numpy as np
import records




def f1_score(y_true, y_pred):
		import keras.backend as K

		# Count positive samples.
		c1 = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
		c2 = K.sum(K.round(K.clip(y_pred, 0, 1)))
		c3 = K.sum(K.round(K.clip(y_true, 0, 1)))

		# If there are no true samples, fix the F1 score at 0.
		if c3 == 0:
		    return 0

		# How many selected items are relevant?
		precision = c1 / c2

		# How many relevant items are selected?
		recall = c1 / c3

		# Calculate f1_score
		f1_score = 2 * (precision * recall) / (precision + recall)
		return f1_score

class ErrorClassifier():
	#slice can be an array containing any element between "entity", "slot", "prev" or "all"

	def __init__(self, BoW =None, featurize_confidence = "none", entity_check=False, 
					  input_feature_map=None, slice_vec=["entity"], 
					  prev_turn_context = 0,
					  labels={"none": 0, "dm": 1, "nlu": 2,  "both": 3},
					  one_hot={"none": [1,0,0,0], "dm": [0,1,0,0], "nlu": [0,0,1,0], "both": [0,0,0,1]}):
		self.labels = labels
		self.one_hot = one_hot

		self.input_feature_map = input_feature_map
		self.slice_vec = slice_vec
		self.prev_turn_context = prev_turn_context
		self.BoW = BoW
		self.previous_turn = -1
		self.featurize_confidence = featurize_confidence
		self.db = records.Database("mysql://root:root@localhost:3306/movies")
		
		self.entity_check = entity_check

	def fit(self, dataset):
		pass

	def predict(self, x):
		pass

	def calculate_feat_num(self):
		tot = 0
		for f in self.input_feature_map.keys():
			if f.split("_")[0] in self.slice_vec:
				tot += 1

		return tot 

	def calculate_ent_num(self):
		tot = 0
		for f in self.input_feature_map.keys():
			if f.split("_")[0] == "entity":
				tot += 1

		return tot 


	def reset_turn_memory(self):
		n_feats = self.calculate_feat_num()
		if self.BoW != False:
			n_feats += len(self.BoW.vocabulary_)

		if self.entity_check == True:
			n_feats += self.calculate_ent_num()

		if self.featurize_confidence == "all":
			n_feats += 2
		elif self.featurize_confidence == "entity" or self.featurize_confidence == "act":
			n_feats += 1

		self.prev_turns = [np.zeros(n_feats) for x in range(self.prev_turn_context)]
		self.previous_turn = -1

	def contextualize_turn(self, x, turn_number):
		if self.prev_turn_context > 0:
			if turn_number != self.previous_turn + 1:
				self.reset_turn_memory()
				

			to_prepend = np.array(self.prev_turns).flatten()

			contextualized_turn = np.append(to_prepend, x, axis=0)	
			del self.prev_turns[0]
			self.prev_turns.append(np.array(x).reshape(1,-1).flatten())
			self.previous_turn = turn_number
			return contextualized_turn.flatten()
		else:
			return x

	def _lookforact(self, act):
		for k,v in self.input_feature_map.items():
			if k == "prev_{}".format(act):
				return v
		return -1

	def check_bow(self, X):
		if self.BoW:
			self.BoW = self.calculate_BOW(X)

	def calculate_BOW(self, dev_set):
		from sklearn.feature_extraction.text import CountVectorizer

		sentences = []
		for turn in dev_set:
			sentences.append(turn[0]['text'])

		vectorizer = CountVectorizer()
		vectorizer.fit(sentences)
		return vectorizer

	def get_BoWfeats(self, text):
		return np.array(self.BoW.transform([text]).toarray())

	def add_BOW(self, curr_feats, turn):
		bow_feats = self.get_BoWfeats(turn[0]['text']).reshape(-1)
		return np.append(curr_feats, bow_feats, axis=0)

	def combine_steps(self, turn):
		res = np.zeros(len((turn[0]['feat_vec_notflattened'][-1][-1]).flatten()))
		ind_acts = []

		for st in turn:
			np.logical_or(st['feat_vec_notflattened'][-1][-1].flatten(), res, res)
			ind_acts.append(self._lookforact(st['act']['act']))

		for i in ind_acts:
			res[i] = 1

		to_ret = self.slice_values(res.flatten())
		return to_ret, turn[0]['number']

	def add_confidence_features(self, curr_feats, turn, conf="entity"):
		conf_feats = np.array([])

		if conf == "entity" or conf == "all":
			ent_avg = 0.0
			for j,ent in enumerate(turn[0]['entities']):
				ent_avg += ent['confidence']
			ent_avg = np.float64(ent_avg / (j + 1)).reshape(-1) if len(turn[0]['entities']) > 0 else np.float64(0.0).reshape(-1)
			conf_feats = np.append(conf_feats, ent_avg, axis=0)
		
		if conf == "act" or conf == "all":
			act_avg = 0.0
			for j,st in enumerate(turn):
				act_avg += st['act']['confidence']

			act_avg = np.float64(act_avg / (j + 1)).reshape(-1)

			conf_feats = np.append(conf_feats, act_avg, axis=0)

		return np.append(curr_feats, conf_feats, axis=0)

	def add_entity_check(self, curr_feats, turn):
		
		def clean(v):
			v = str(v).replace("'", r"\'")
			return v

		n_entities = len([x for x in self.input_feature_map if x.split("_")[0] == "entity"])
		ent_feats = np.zeros(n_entities)
		

		_query = "SELECT * FROM `{}` WHERE {}"
		
		for ent in turn[0]['entities']:
			if len(ent['entity'].split("::")) > 1:

				table_name = ent['entity'].split("::")[0]
				col_name = ent['entity'].split("::")[1]
				value = ent['value']
				
				constr = {col_name: value}

				query = _query.format(table_name, 
								 " AND ".join(["`{}` = '{}'".format(k, clean(v)) 									\
								 		   for k, v in constr.items()]))

				res = self.db.query(query).as_dict()
				feat_index = self.input_feature_map["entity_{}".format(ent['entity'])]
				ent_feats[feat_index] = 1 if len(res) > 0 else 0

		
		return np.append(curr_feats, ent_feats, axis=0)


	def featurize_turn(self, turn):
		new_turn, turn_number = self.combine_steps(turn)
		if self.BoW != False:
			new_turn = self.add_BOW(new_turn, turn)

		if self.featurize_turn != "none":
			new_turn = self.add_confidence_features(new_turn, turn, conf=self.featurize_confidence)

		if self.entity_check == True:
			new_turn = self.add_entity_check(new_turn, turn)

		return np.array(new_turn).flatten(), self.labels[turn[0]['error']], turn_number
 

	def slice_values(self,x):
		to_del_indeces = []
		if self.slice_vec == "all":
			return x
		else:

			for i,(x_feat, ind_feat) in enumerate(zip(x, self.input_feature_map.keys())):
				if ind_feat.split("_")[0] not in self.slice_vec:
					to_del_indeces.append(i)

		return np.array([x_feat for i, x_feat in enumerate(x) if i not in to_del_indeces])

	def slice_flattened(self,x, context_window):
		len_unit = int(len(x) / context_window)
		new_x = []
		for unit in range(context_window):
			new_x.append(self.slice_values(x[0+(unit*len_unit): len_unit+(unit * len_unit)]))

		return np.array(new_x).flatten()

	def closeDB(self):
		self.db.close()

class RandomClassifier(ErrorClassifier):
	#random predict an element from labels, according to given probabilities
	
	import operator

	def __init__(self, input_feature_map=None, slice_vec=["entity"], 
		 BoW =None,  
		prev_turn_context = 0,
		probabilities=[0.25, 0.25, 0.25, 0.25], 
		labels={"none": 0, "dm": 1, "nlu": 2,  "both": 3}, 
		one_hot={"none": [1,0,0,0], "dm": [0,1,0,0], "nlu": [0,0,1,0], "both": [0,0,0,1]}):

		super(RandomClassifier, self).__init__( BoW =BoW,  prev_turn_context=prev_turn_context,input_feature_map=input_feature_map, slice_vec=slice_vec,labels=labels, one_hot=one_hot)
		self.probability_distrib = probabilities

	def predict(self,x):
		from numpy.random import choice
		return choice([v for k,v in self.labels.items()], 1, p=self.probability_distrib)[0]

class ThresholdClassifier(ErrorClassifier):
	#Classifier based on two thresholds T1 and T2. T1 works on DM level confidences, T2 on NLU confidences instead.
	# Those thresholds can be learnt from a set or set manually

	def __init__(self,T1=0.9, T2=0.65,
		 input_feature_map=None, slice_vec=["entity"], 
		  BoW =None,  
		 prev_turn_context = 0,
		labels={"none": 0, "dm": 1, "nlu": 2,  "both": 3}, 
		one_hot={"none": [1,0,0,0], "dm": [0,1,0,0], "nlu": [0,0,1,0], "both": [0,0,0,1]}):

		super(ThresholdClassifier, self).__init__( BoW =BoW,  prev_turn_context = prev_turn_context,input_feature_map=input_feature_map, slice_vec=slice_vec, labels=labels, one_hot=one_hot)
		self.T1 = T1
		self.T2 = T2

	

	def learn_thresholds(self, X):
		sum_nlu = 0
		n_nlu = 0
		sum_dm = 0
		n_dm = 0
		for turn in X:
			for ent in turn[0]['entities']:
				sum_nlu += ent['confidence']
				n_nlu += 1
			for st in turn:
				sum_dm += st['act']['confidence']
				n_dm += 1
		self.T2 = float(sum_nlu/n_nlu)
		self.T1 = float(sum_dm/n_dm)



	def predict(self, x):
		#x is a turn as serie of M variable steps
		#The N steps are always in the form user:system:system:... 
		#The NLU thresholder only checks the entities at the first step
		#The DM thresholder checks all the steps since they are needed for the action prediction

		error = 0 #none error
		sum_NLU_conf = 0
		n_ents = 0

		for ent in x[0]['entities']:
			if "confidence" in ent.keys():
				sum_NLU_conf += ent['confidence']
				n_ents += 1

		avg_NLU_conf = sum_NLU_conf/n_ents if n_ents > 0 else 1
		error = self.labels['nlu'] if avg_NLU_conf < self.T2 else self.labels['none']

		sum_DM_conf = 0
		n_acts = 0
		for step in x:
			sum_DM_conf += step['act']['confidence']
			n_acts += 1

		avg_DM_conf = sum_DM_conf/n_acts
		if error == self.labels['nlu'] and avg_DM_conf < self.T1:
			error = self.labels['both']
		elif error == self.labels['none'] and avg_DM_conf < self.T2:
			error = self.labels['dm']
		return error

class BinaryThresholdClassifier(ThresholdClassifier):

	def __init__(self,T1=0.9, T2=0.65,
		input_feature_map=None, slice_vec=["entity"],
		prev_turn_context = 0, 
		 BoW =None,  
		labels={"none": 0, "error": 1}, 
		one_hot={"none": [0], "error": [1]}):

		super(BinaryThresholdClassifier, self).__init__( BoW =BoW, T1=T1, T2=T2, prev_turn_context = prev_turn_context,input_feature_map=input_feature_map, slice_vec=slice_vec, labels=labels, one_hot=one_hot)

	def predict(self,x):

		error = 0 #none error
		sum_NLU_conf = 0
		n_ents = 0

		for ent in x[0]['entities']:
			if "confidence" in ent.keys():
				sum_NLU_conf += ent['confidence']
				n_ents += 1

		avg_NLU_conf = sum_NLU_conf/n_ents if n_ents > 0 else 1
		
		sum_DM_conf = 0
		n_acts = 0
		for step in x:
			sum_DM_conf += step['act']['confidence']
			n_acts += 1

		avg_DM_conf = sum_DM_conf/n_acts

		error = self.labels['error'] if avg_NLU_conf < self.T2 or avg_DM_conf < self.T1	 else self.labels['none']
		return error


class MajorityModel(ErrorClassifier):

	def __init__(self,
		input_feature_map=None, slice_vec=["entity"], 
		prev_turn_context = 0,
		 BoW =None,  
		labels={"none": 0, "dm": 1, "nlu": 2,  "both": 3}, 
		one_hot={"none": [1,0,0,0], "dm": [0,1,0,0], "nlu": [0,0,1,0], "both": [0,0,0,1]}):

		super(MajorityModel, self).__init__( BoW =BoW,  prev_turn_context = prev_turn_context,input_feature_map=input_feature_map, slice_vec=slice_vec, labels=labels, one_hot=one_hot)
		self.majority_class = None

	def fit(self, X):
		import operator
		#X is array of turns as arrays of steps
		

		class_counters = dict((el,0) for el in self.labels.keys())
		for x in X:
			class_counters[x[0]['error']] += 1

		self.majority_class = self.labels[max(class_counters.items(), key=operator.itemgetter(1))[0]]


	def predict(self,x):
		return self.majority_class

class SKLearnClassifier(ErrorClassifier):
	def __init__(self, clf,featurize_confidence = "none", entity_check=False, 
		context_window=1,
		BoW =None,  
		input_feature_map=None, slice_vec=["entity"], 
		prev_turn_context = 0,
		labels={"none": 0, "dm": 1, "nlu": 2,  "both": 3}, 
		one_hot={"none": [1,0,0,0], "dm": [0,1,0,0], "nlu": [0,0,1,0], "both": [0,0,0,1]}):

		self.clf = clf
		self.context = context_window
		super(SKLearnClassifier, self).__init__( BoW =BoW, entity_check=entity_check, featurize_confidence=featurize_confidence,
												 prev_turn_context=prev_turn_context, input_feature_map=input_feature_map, 
												 slice_vec=slice_vec,labels=labels, one_hot=one_hot)
	

	def fit(self, X):
		turns = []
		y_turns = []
		tmp_turn = None
		self.check_bow(X)
		if self.prev_turn_context > 0:
			self.reset_turn_memory()
		for turn in X:

			new_turn, y_turn, turn_number = self.featurize_turn(turn)
			tmp_turn = self.contextualize_turn(new_turn, turn_number)
			turns.append(tmp_turn)
			y_turns.append(y_turn)


		self.clf.fit(turns, y_turns)

	def fit_no_comp(self, featurized_turns, y_turns, turns):
		self.check_bow(turns)
		if self.prev_turn_context > 0:
			self.reset_turn_memory()
		self.clf.fit(featurized_turns, y_turns)


	def dump_train(self, X):
		turns = []
		y_turns = []
		tmp_turn = None
		self.check_bow(X)
		if self.prev_turn_context > 0:
			self.reset_turn_memory()
		for turn in X:
			new_turn, y_turn, t_n= self.featurize_turn(turn)
			tmp_turn = self.contextualize_turn(new_turn, t_n)
			turns.append(tmp_turn)
			y_turns.append(y_turn)
		return turns, y_turns

	def predict(self, X):
		new_turn, y, turn_number= self.featurize_turn(X)
		new_turn = self.contextualize_turn(new_turn, turn_number)
		pred = self.clf.predict([new_turn])
		return pred[0]


"""
class Logit(ErrorClassifier):

	def __init__(self, C=2, solver="liblinear",
		context_window=1,
		 BoW =None,  
		input_feature_map=None, slice_vec=["entity"], 
		prev_turn_context = 0,
		labels={"none": 0, "dm": 1, "nlu": 2,  "both": 3}, 
		one_hot={"none": [1,0,0,0], "dm": [0,1,0,0], "nlu": [0,0,1,0], "both": [0,0,0,1]}):

		from sklearn.linear_model import LogisticRegression

		self.clf = LogisticRegression(C=C, solver=solver)
		self.context = context_window
		super(Logit, self).__init__( BoW =BoW,  prev_turn_context=prev_turn_context, input_feature_map=input_feature_map, slice_vec=slice_vec,labels=labels, one_hot=one_hot)

	def fit(self, X):
		turns = []
		y_turns = []
		tmp_turn = None
		for turn in X:
			new_turn, y_turn, turn_number = self.featurize_turn(turn)
			tmp_turn = self.contextualize_turn(new_turn, turn_number)
			turns.append(tmp_turn)
			y_turns.append(y_turn)


		self.clf.fit(turns, y_turns)

	def dump_train(self, X):
		turns = []
		y_turns = []
		tmp_turn = None
		for turn in X:
			new_turn, y_turn, t_n= self.featurize_turn(turn)
			tmp_turn = self.contextualize_turn(new_turn, t_n)
			turns.append(tmp_turn)
			y_turns.append(y_turn)
		return turns, y_turns

	def predict(self, X):
		new_turn, y, turn_number= self.featurize_turn(X)
		new_turn = self.contextualize_turn(new_turn, turn_number)
		pred = self.clf.predict([new_turn])
		return pred[0]

	def dump(self, folder="models/"):
		with open("{}{}".format(folder, "logit"), "wb+") as f:
			pickle.dump(self.__dict__,f)

	def load(self, folder="models/"):       
		with open("{}{}".format(folder, "logit"), "rb") as f:
			self.__dict__.update(pickle.load(f))

		


class LinearSVM(ErrorClassifier):
	#c = 2, C_W = 3

	def __init__(self, C=2, context_window=1,
		 BoW =None,  
		input_feature_map=None, slice_vec=["entity"], 
		prev_turn_context = 0,
		labels={"none": 0, "dm": 1, "nlu": 2,  "both": 3}, 
		one_hot={"none": [1,0,0,0], "dm": [0,1,0,0], "nlu": [0,0,1,0], "both": [0,0,0,1]}):

		from sklearn.svm import LinearSVC

		self.clf = LinearSVC(C=C)
		self.context = context_window
		super(LinearSVM, self).__init__( BoW =BoW,  prev_turn_context=prev_turn_context, input_feature_map=input_feature_map, slice_vec=slice_vec,labels=labels, one_hot=one_hot)
		

	def fit(self, X):
		turns = []
		y_turns = []
		tmp_turn = None
		for turn in X:
			new_turn, y_turn, turn_number = self.featurize_turn(turn)
			tmp_turn = self.contextualize_turn(new_turn, turn_number)
			turns.append(tmp_turn)
			y_turns.append(y_turn)


		self.clf.fit(turns, y_turns)

	def dump_train(self, X):
		turns = []
		y_turns = []
		tmp_turn = None
		for turn in X:
			new_turn, y_turn, t_n= self.featurize_turn(turn)
			tmp_turn = self.contextualize_turn(new_turn, t_n)
			turns.append(tmp_turn)
			y_turns.append(y_turn)
		return turns, y_turns

	def predict(self, X):
		new_turn, y, turn_number= self.featurize_turn(X)
		new_turn = self.contextualize_turn(new_turn, turn_number)
		pred = self.clf.predict([new_turn])
		return pred[0]

	def dump(self, folder="models/"):
		with open("{}{}".format(folder, "linear_SVM_3"), "wb+") as f:
			pickle.dump(self.__dict__,f)

	def load(self, folder="models/"):       
		with open("{}{}".format(folder, "linear_SVM_3"), "rb") as f:
			self.__dict__.update(pickle.load(f))

class KernelSVM(LinearSVM):
	#c = 2, C_W = 3

	def __init__(self, C=2, gamma="auto", context_window=1, kernel="rbf",
		 BoW =None,  
		input_feature_map=None, slice_vec=["entity"], 
		prev_turn_context = 0,
		labels={"none": 0, "dm": 1, "nlu": 2,  "both": 3}, degree=3,
		one_hot={"none": [1,0,0,0], "dm": [0,1,0,0], "nlu": [0,0,1,0], "both": [0,0,0,1]}):

		from sklearn.svm import SVC

		#super(LinearSVM, self).__init__(labels=labels, one_hot=one_hot)
		self.labels = labels
		self.one_hot = one_hot
		self.clf = SVC(C=C, kernel=kernel, gamma=gamma, degree=degree)
		self.context = context_window

		self.slice_vec = slice_vec
		if input_feature_map:
			self.input_feature_map = input_feature_map
		else:
			with open("input_feature_map.pck", "rb") as f:
				self.input_feature_map = pickle.read(f)
		self.prev_turn_context = prev_turn_context
		self.BoW = BoW
		self.reset_turn_memory()
		self.previous_turn = -1


	def dump(self, folder="models/"):
		with open("{}{}".format(folder, "linear_SVM_3"), "wb+") as f:
			pickle.dump(self.__dict__,f)

	def load(self, folder="models/"):       
		with open("{}{}".format(folder, "linear_SVM_3"), "rb") as f:
			self.__dict__.update(pickle.load(f))


class ErrorLSTM(ErrorClassifier):

	def __init__(self, context_window=3, num_features = 122, n_hidden=50,
		input_feature_map=None, slice_vec=["entity"], 
		 BoW =None,  
		prev_turn_context = 0,
		labels={"none": 0, "dm": 1, "nlu": 2,  "both": 3}, 
		one_hot={"none": [1,0,0,0], "dm": [0,1,0,0], "nlu": [0,0,1,0], "both": [0,0,0,1]}, n_classes=4):
		import keras


		super(ErrorLSTM, self).__init__( BoW =BoW,prev_turn_context = prev_turn_context,input_feature_map=input_feature_map, slice_vec=slice_vec,labels=labels, one_hot=one_hot)
		self.graph = keras.backend.tf.get_default_graph()
		self.context = context_window
		self.number_feats = num_features
		self.hidden_neurons = n_hidden
		self.n_classes = n_classes
		self.model = self.model_architecture()
		#print(self.model.summary())

	
	def featurize_turn(self, turn):
		new_turn = []
		to_prepend = 0
		step_len = len(self.slice_values(turn[0]['feat_vec_notflattened'][-1][-1]).flatten())
		tot_appended = 0
		if len(turn) < self.context:
			to_prepend  = self.context - len(turn)
			for i in range(to_prepend):
				new_turn.append(np.zeros(step_len))
				tot_appended+= 1

			for s in range(len(turn)):
				new_turn.append(self.slice_values(turn[s]['feat_vec_notflattened'][-1][-1]).flatten())
				tot_appended += 1
			
		else:
			for i in range(self.context):
				new_turn.append(self.slice_values(turn[i]['feat_vec_notflattened'][-1][-1]).flatten())
				tot_appended += 1

		return np.array(new_turn), np.array(self.one_hot[turn[0]['error']])

	def model_architecture(self):
		from keras.layers import LSTM, Activation, Masking, Dense
		from keras.models import Sequential

		model = Sequential()
		model.add(LSTM(self.hidden_neurons, input_shape=(self.context, self.calculate_feat_num() )))
		model.add(Dense(units = self.n_classes,activation='sigmoid'))
		if self.n_classes > 1:
			model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy', f1_score])
		else:
			model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy', f1_score])

		return model

	def fit(self,X):
		turns = []
		y_turns = []
		for turn in X:
			new_turn, y_turn = self.featurize_turn(turn)
			turns.append(new_turn)
			y_turns.append(y_turn)

		self.model.fit(np.array(turns), np.array(y_turns), batch_size=10, epochs=30)

	def predict(self, X):
		new_turn, y = self.featurize_turn(X)
		pred = self.model.predict(np.array(new_turn).reshape(1, self.context,  -1))
		return pred[0]

class ShallowNN(ErrorClassifier):

	def __init__(self, context_window=3, num_features = 122, n_hidden=300,
		labels={"none": 0, "dm": 1, "nlu": 2,  "both": 3}, 
		one_hot={"none": [1,0,0,0], "dm": [0,1,0,0], "nlu": [0,0,1,0], "both": [0,0,0,1]}, n_classes=4):
		import keras


		super(ShallowNN, self).__init__(labels=labels, one_hot=one_hot)
		self.graph = keras.backend.tf.get_default_graph()
		self.context = context_window
		self.number_feats = num_features
		self.hidden_neurons = n_hidden
		self.n_classes = n_classes
		self.model = self.model_architecture()
		#print(self.model.summary())

	

	def featurize_turn(self, turn):
		new_turn = []
		to_prepend = 0
		#step_len = len(turn[0]['feat_vec_notflattened'][-1][-1].flatten())
		step_len = len(turn[0]['feat_vec_notflattened'][-1][-1].flatten())
		tot_appended = 0
		if len(turn) < self.context:
			to_prepend  = self.context - len(turn)
			for i in range(to_prepend):
				new_turn.extend(np.zeros(step_len))
				tot_appended+= 1

			for s in range(len(turn)):

				new_turn.extend(turn[s]['feat_vec_notflattened'][-1][-1].flatten())
				tot_appended += 1
			
		else:
			for i in range(self.context):
				new_turn.extend(turn[i]['feat_vec_notflattened'][-1][-1].flatten())
				tot_appended += 1

		return np.array(new_turn).flatten(), self.labels[turn[0]['error']]

	def model_architecture(self):
		from keras.layers import Dense
		from keras.models import Sequential

		model = Sequential()
		model.add(Dense(self.hidden_neurons, input_dim=self.number_feats * self.context, activation="relu"))
		model.add(Dense(self.n_classes,activation='sigmoid'))
		if self.n_classes > 1:
			model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
		else:
			model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

		return model

	def fit(self,X):
		turns = []
		y_turns = []
		for turn in X:
			new_turn, y_turn = self.featurize_turn(turn)
			turns.append(new_turn)
			y_turns.append(y_turn)
		self.model.fit(np.array(turns), np.array(y_turns), batch_size=2, epochs=20)

	def predict(self, X):
		new_turn, y = self.featurize_turn(X)
		pred = self.model.predict(np.array(new_turn).reshape(1,-1))
		return pred[0]
"""

