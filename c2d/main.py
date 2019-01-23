from factories 	import FrameFactory, GoalFactory
from simulator 	import Sim, UserGoal
from database 	import Database
from manager 	import InteractionManager
from trainer 	import DialogManagerTrainer, FullAgentTrainer, Seq2ActionAgentTrainer
from agent 		import DM, Frame
from nlg 		import RuleBasedEngine

#from utils.logger import Logger
#from utils.dumper import Dumper

from threading import Thread
import argparse
import json

def get_standard_profile_parameters(n):
	return [{'informativity_sd' : 2.0,
			 'informativity_mu' : 1,
			 'cooperation' : 1.0,
			 'flexibility' : 0.8,
			 'experience'  : 0.8,
			 'indecision'  : 0.1,
			 'ambiguity'   : 0.1} for i in range(n)]

def get_profiles_parameters(n, delta_factor):
	deltas = {'informativity_sd' : 4.5 * delta_factor,
			  'informativity_mu' : 0 * delta_factor,
			  'cooperation' : -1.0 * delta_factor,
			  'flexibility' : -1.0 * delta_factor,
			  'experience' : -1.0 * delta_factor,
			  'indecision' : 1.0 * delta_factor,
			  'ambiguity'  : 1.0 * delta_factor}

	# start with "the perfect user"
	profiles = [{'informativity_sd' : 0.0,
				 'informativity_mu' : 1,
				 'cooperation' : 1.0,
				 'flexibility' : 1.0,
				 'experience' : 1.0,
				 'indecision' : 0.0,
				 'ambiguity' : 0.0}]

	for i in range(n - 1):
		profiles.append({k : v + deltas[k] for k, v in profiles[-1].items()})
	
	return profiles

def generate_dialogs(n, im, dm, sim, trainer, frames, goals, 
								   story_file_name="stories"):
	if n == 0:
		return
		
	profiles = get_standard_profile_parameters(n)
	#profiles = get_profiles_parameters(n, 1.0/n)
	trainer.new_story_file(story_file_name)

	for i in range(n):
		for goal in goals[i]:
			for slot in goal.constraints.keys():
					goal.resample(slot)

		print("[...] generating {} number {}".format(story_file_name, i + 1))
		#logger.log_generation(i + 1, len(frames))
		trainer.new_story(add_newline=(i != 0))

		dm.prepare(frames[i])
		sim.prepare(goals[i], profile_feats=profiles[i])

		dm_thread  = Thread(target=dm.run)
		sim_thread = Thread(target=sim.run)

		dm_thread.start()
		sim_thread.start()

		dm_thread.join()
		sim_thread.join()

def main():

	parser = argparse.ArgumentParser()
	
	parser.add_argument("n", type=int, help="Samples per task")
	parser.add_argument("db_name", help="Name of the database to use")
	parser.add_argument("bot_name", help="Name of the bot folder")
	parser.add_argument("features", help="Path to json file with bot features")

	parser.add_argument("-db_ip", default="localhost", help="Database address")
	parser.add_argument("-db_pwd", default="root", help="User's password")
	parser.add_argument("-db_user", default="root", help="Database user")
	parser.add_argument("-db_port", default="3306", help="Database port")

	parser.add_argument("-log_file", default="/var/www/vui/state.json", 
									 help="Log file to save the state")

	parser.add_argument('-e', '--epochs', default=180, type=int,
						   help="Epochs for training")
	parser.add_argument('-m', '--max_history', default=5, type=int,
							 help="History size feature")
	parser.add_argument('-b', '--batch_size', default=32, type=int,
						   help="Batch size for training")
	parser.add_argument('-v', '--validation_split', default=0.3, type=float, 
						   help="Validation splits for training")

	args = parser.parse_args()
	database = "mysql://{}:{}@{}:{}/{}".format(args.db_user, args.db_pwd, 
								  args.db_ip, args.db_port, args.db_name)

	db = Database.get_instance(database=database)
	#logger = Logger.get_instance(args.log_file)

	frame_factory = FrameFactory()
	goal_factory = GoalFactory()

	with open(args.features, "r") as f:
		tasks = json.load(f)['tasks']

	frames, goals = [], []
	for dial in range(int(args.n)):
		for task in tasks:
			frames.append(frame_factory.build_frames(task))
			goals.append(goal_factory.build_goals(task))

	#trainer = Seq2ActionAgentTrainer(sum(frames, []), database, RuleBasedEngine())
	trainer = FullAgentTrainer(sum(frames, []), database, RuleBasedEngine())
	#trainer = DialogManagerTrainer(sum(frames, []), database)
	
	#dumper = #dumper(args.bot_name, trainer, domain_file_path="/var/www/vui/", 
	#							 virtual_env="/var/www/vui/python_virtualenv/",
	#									 base_path="/var/www/vui/python/BOTs/",
	#										python_path="/var/www/vui/python/")

	im = InteractionManager(trainer)
	dm, sim = DM(im), Sim(im)

	# generate validation dialogs
	n_valid_samples = round(len(frames) * args.validation_split)
	generate_dialogs(n_valid_samples, im, dm, sim, trainer, frames[:n_valid_samples], 
									goals[:n_valid_samples], story_file_name="valid")
	# generate training dialogs
	n_train_samples = len(frames) - n_valid_samples
	generate_dialogs(n_train_samples, im, dm, sim, trainer, frames[n_valid_samples:], 
									goals[n_valid_samples:], story_file_name="story")

	print("[...] building domain.yml...")
	trainer.build_domain_yml()
	if isinstance(trainer, FullAgentTrainer):
		print("[...] building nlu training file...")
		trainer.build_phrases_file()
		print("[...] building dialogs.json file...")
		trainer.build_file_for_hit()
		print("[...] cleaning transcript file...")
		trainer.build_raw_transcript()
	if isinstance(trainer, Seq2ActionAgentTrainer):
		print("[...] building user lexicon file...")
		trainer.build_user_lexicon()
		print("[...] computing sentence embeddings...")
		trainer.compute_sentence_embeddings()

	#dumper.dump_model()
	
	#logger.log_data_preprocessing()
	#dumper.generate_testset(int(20 * len(frames) / 100))
	#dumper.train_model(epochs=args.epochs, batch_size=args.batch_size, 
	#						    validation_split=args.validation_split, 
	#						              max_history=args.max_history)
	
	#logger.log_start_testing()
	#dumper.test_model() 

if __name__ == "__main__":
	main()