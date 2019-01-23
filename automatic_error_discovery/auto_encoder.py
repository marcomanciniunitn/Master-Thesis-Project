import sys
import os
stderr = sys.stderr
sys.stderr = open(os.devnull, 'w')
import keras
sys.stderr = stderr

from pyod.models.auto_encoder import AutoEncoder
from pyod.utils.data import generate_data
from pyod.utils.data import evaluate_print
from keras.losses import mean_squared_error
from sklearn.utils import check_array
from sklearn.preprocessing import StandardScaler
import numpy as np

from SL_models import ErrorClassifier
from pyod_master.pyod.utils.utility import check_parameter
from pyod_master.pyod.utils.stat_models import pairwise_distances_no_broadcast
from sklearn.utils.validation import check_is_fitted



# noinspection PyUnresolvedReferences,PyPep8Naming,PyTypeChecker
class MyAutoEncoder(AutoEncoder, ErrorClassifier):
  

    def __init__(self, hidden_neurons=[32],
                 hidden_activation='relu', output_activation='sigmoid',
                 loss=mean_squared_error, optimizer='adam',
                 epochs=30, batch_size=10, dropout_rate=0.1,
                 l2_regularizer=0.2, validation_size=0.1, preprocessing=True,
                 verbose=0, random_state=None, contamination=0.1,

                 BoW=None, featurize_confidence = "none", entity_check=False, 
                 prev_turn_context=0, input_feature_map=None, slice_vec=[], 
                 labels={"none": 0, "error": 1}, 
                 one_hot={"none": [0], "error": [1]}):
        
        AutoEncoder.__init__(self, hidden_neurons=hidden_neurons, 
                 hidden_activation=hidden_activation, output_activation=output_activation,
                 loss=mean_squared_error, optimizer=optimizer,
                 epochs=epochs, batch_size=batch_size, dropout_rate=dropout_rate,
                 l2_regularizer=l2_regularizer, validation_size=validation_size, preprocessing=preprocessing,
                 verbose=verbose, random_state=random_state, contamination=contamination)

        ErrorClassifier.__init__(self, BoW =BoW,  featurize_confidence=featurize_confidence, entity_check=entity_check, 
                                 prev_turn_context=prev_turn_context, input_feature_map=input_feature_map, 
                                 slice_vec=slice_vec,labels=labels, one_hot=one_hot)

    def fit_no_comp(self, __featurized_turns, __y_turns, turns):
        self.check_bow(turns)
        if self.prev_turn_context > 0:
            self.reset_turn_memory()
        X = check_array(__featurized_turns)
        self._set_n_classes(None)

        # Verify and construct the hidden units
        self.n_samples_, self.n_features_ = X.shape[0], X.shape[1]

        # Standardize data for better performance
        if self.preprocessing:
            self.scaler_ = StandardScaler()
            X_norm = self.scaler_.fit_transform(X)
        else:
            X_norm = np.copy(X)

        # Shuffle the data for validation as Keras do not shuffling for
        # Validation Split
        np.random.shuffle(X_norm)

        # Validate and complete the number of hidden neurons
        if np.min(self.hidden_neurons) > self.n_features_:
            self.hidden_neurons = [self.hidden_neurons]
            #raise ValueError("The number of neurons should not exceed "
            #                 "the number of features")
        self.hidden_neurons_.insert(0, self.n_features_)

        # Calculate the dimension of the encoding layer & compression rate
        self.encoding_dim_ = np.median(self.hidden_neurons)
        self.compression_rate_ = self.n_features_ // self.encoding_dim_

        # Build AE model & fit with X
        self.model_ = self._build_model()
        self.history_ = self.model_.fit(X_norm, X_norm,
                                        epochs=self.epochs,
                                        batch_size=self.batch_size,
                                        shuffle=True,
                                        validation_split=self.validation_size,
                                        verbose=self.verbose).history
        # Reverse the operation for consistency
        self.hidden_neurons_.pop(0)
        # Predict on X itself and calculate the reconstruction error as
        # the outlier scores. Noted X_norm was shuffled has to recreate
        if self.preprocessing:
            X_norm = self.scaler_.transform(X)
        else:
            X_norm = np.copy(X)

        pred_scores = self.model_.predict(X_norm)
        self.decision_scores_ = pairwise_distances_no_broadcast(X_norm,
                                                                pred_scores)
        self._process_decision_scores()
        return self 

    # noinspection PyUnresolvedReferences
    def fit(self, X, y=None):

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

        # Validate inputs X and y (optional)
        X = check_array(turns)
        self._set_n_classes(None)

        # Verify and construct the hidden units
        self.n_samples_, self.n_features_ = X.shape[0], X.shape[1]

        # Standardize data for better performance
        if self.preprocessing:
            self.scaler_ = StandardScaler()
            X_norm = self.scaler_.fit_transform(X)
        else:
            X_norm = np.copy(X)

        # Shuffle the data for validation as Keras do not shuffling for
        # Validation Split
        np.random.shuffle(X_norm)

        # Validate and complete the number of hidden neurons
        if np.min(self.hidden_neurons) > self.n_features_:
            self.hidden_neurons = [self.hidden_neurons]
            #raise ValueError("The number of neurons should not exceed "
            #                 "the number of features")
        self.hidden_neurons_.insert(0, self.n_features_)

        # Calculate the dimension of the encoding layer & compression rate
        self.encoding_dim_ = np.median(self.hidden_neurons)
        self.compression_rate_ = self.n_features_ // self.encoding_dim_

        # Build AE model & fit with X
        self.model_ = self._build_model()
        self.history_ = self.model_.fit(X_norm, X_norm,
                                        epochs=self.epochs,
                                        batch_size=self.batch_size,
                                        shuffle=True,
                                        validation_split=self.validation_size,
                                        verbose=self.verbose).history
        # Reverse the operation for consistency
        self.hidden_neurons_.pop(0)
        # Predict on X itself and calculate the reconstruction error as
        # the outlier scores. Noted X_norm was shuffled has to recreate
        if self.preprocessing:
            X_norm = self.scaler_.transform(X)
        else:
            X_norm = np.copy(X)

        pred_scores = self.model_.predict(X_norm)
        self.decision_scores_ = pairwise_distances_no_broadcast(X_norm,
                                                                pred_scores)
        self._process_decision_scores()
        return self

    def predict(self, X):
        """Predict if a particular sample is an outlier or not.

        :param X: The input samples
        :type X: numpy array of shape (n_samples, n_features)

        :return: For each observation, tells whether or not
            it should be considered as an outlier according to the fitted
            model. 0 stands for inliers and 1 for outliers.
        :rtype: array, shape (n_samples,)
        """
        new_turn, y, turn_number= self.featurize_turn(X)
        new_turn = self.contextualize_turn(new_turn, turn_number)


        check_is_fitted(self, ['decision_scores_', 'threshold_', 'labels_'])

        pred_score = self.decision_function(new_turn)
        return (pred_score > self.threshold_).astype('int').ravel()

    def decision_function(self, X):
        check_is_fitted(self, ['model_', 'history_'])
        X = X.reshape(1, -1)
        X = check_array(X)

        if self.preprocessing:
            X_norm = self.scaler_.transform(X)
        else:
            X_norm = np.copy(X)

        # Predict on X and return the reconstruction errors
        pred_scores = self.model_.predict(X_norm)
        return pairwise_distances_no_broadcast(X_norm, pred_scores)