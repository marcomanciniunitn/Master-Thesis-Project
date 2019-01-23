import json
import argparse
import keras
import os

class Log_Callback(keras.callbacks.Callback):

    def __init__(self, tot_epochs, log_file):
        keras.callbacks.Callback()
        self.tot_epochs = tot_epochs
        self.log_file = log_file

    def on_train_begin(self, logs={}):
        state = {"state": "Training", "text": "The training is started right now!"}
        with open(self.log_file, "w+") as f:
            json.dump(state, f)

 
    def on_train_end(self, logs={}):
    	state = {"state": "Testing", "text": "Testing is just started"}
    	with open(self.log_file,  "w+") as f:
    		json.dump(state, f)
        


    def on_epoch_begin(self, epochs, logs={}):
        state = {"state": "Training", "text": "{}/{} epochs".format(epochs, self.tot_epochs)}
        with open(self.log_file, "w+") as f:
            json.dump(state, f)

 
    def on_epoch_end(self, epoch, logs={}):
        state = {"state": "Training", "text": "{}/{} epochs".format(epoch, self.tot_epochs)}
        with open(self.log_file, "w+") as f:
            json.dump(state, f)

 
    def on_batch_begin(self, batch, logs={}):
        return
 
    def on_batch_end(self, batch, logs={}):
        return


class Logger():


	class __Logger:
		def __init__(self, log_file):
			if os.path.isfile(log_file):
				os.remove(log_file)
			Logger.log_file = log_file
			
			Logger.state = {"state": "generating", "text": "0/0 dialogues generated"}
			

	__instance = None


	def __init__(self, log_file):
		if not Logger.__instance: 
			Logger.__instance = Logger.__Logger(log_file)

	@staticmethod
	def get_instance(log_file):
		return Logger(log_file)
	


	def log_generation(self, current, total):
		Logger.state = {"state": "generating", "text": "{}/{} dialogues generated".format(current, total)}
		with open(Logger.log_file, "w+") as f:
			json.dump(Logger.state, f)
			
	def log_data_preprocessing(self):
		Logger.state = {"state": "Training", "text": "Preparing the data for the training <br /> (can take a while)"}
		with open(Logger.log_file,  "w+") as f:
			json.dump(Logger.state, f)

	def log_start_testing(self):
		Logger.state = {"state": "Testing", "text": "Testing is just started"}
		with open(Logger.log_file,  "w+") as f:
			json.dump(Logger.state, f)

	def log_end_testing(self,aer):
		Logger.state = {"state": "Testing", "text": "The Action Error Rate (AER) is: {}".format(aer)}
		with open(Logger.log_file,  "w+") as f:
			json.dump(Logger.state, f)

	def get_KerasCB(self, epochs):
		return Log_Callback(epochs, Logger.log_file)



