from trainer import VUIdmTrainer

from distutils.dir_util import copy_tree
import os
from shutil import copyfile
from shutil import move

class Dumper():

	def __init__(self, model_directory, trainer, domain_file_path="/var/www/vui/", base_path="/var/www/vui/python/BOTs/",
		python_path="/var/www/vui/python/", virtual_env="/var/www/vui/python_virtualenv/"):
		#base path for store models (e.g /var/www/vui/python/BOTs/)
		self.base_path = base_path
		#directory name for the model
		self.model_directory = model_directory
		#base folder containing the generated domain file
		self.domain_file_path = domain_file_path
		#path for folder containing the python code (e.g database.py and templateVUI.dm)
		self.python_path = python_path
		self.model_path = "{}{}".format(base_path, model_directory)

		self.trainer = trainer
		self.virtual_env = virtual_env


	def dump_model(self):
		if not os.path.exists(self.model_path):
		    os.makedirs(self.model_path)

		copy_tree("{}{}".format(self.python_path, "template_VUI.dm"), self.model_path)
		copyfile("{}{}".format(self.python_path, "database.py"), "{}/{}".format(self.model_path,"/database.py"))
		
		move("{}{}".format(self.domain_file_path, self.trainer.actions_f), "{}/{}".format(self.model_path, self.trainer.actions_f))
		move("{}{}".format(self.domain_file_path, self.trainer.domain_f), "{}/{}".format(self.model_path, "config/domain.yml"))
		move("{}{}".format(self.domain_file_path, self.trainer.stories_f), "{}/{}".format(self.model_path, "data/story.md"))

		

	def train_model(self, epochs=200, batch_size=100, validation_split=0.2, max_history=5):
		os.system("{}bin/python3 {}/bot.py dm -e {} -b {} -v {} -m {}".format(self.virtual_env, self.model_path, epochs, 
																									batch_size, validation_split, 
																									max_history))
	def generate_testset(self, size):
		data_path = "{}/{}".format(self.model_path, "data/")

		with open("{}{}".format(data_path, "story.md"), "r") as f:
			lines = f.readlines()
		print(len(lines))

		index = 0
		test = []
		glob_index = 0
		for line in lines:
			if "## story_" in line:
				index = index + 1
			if index == size:
				print("dentro")
				with open("{}{}".format(data_path, "test.md"), "w+") as f:
					f.writelines(test)
					break
			test.append(line)
			glob_index += 1

		with open("{}{}".format(data_path, "story.md"), "w+") as f:
			f.writelines(lines[glob_index:])


	def test_model(self):

		cmd = "{}bin/python3 -m rasa_core.evaluate -s {}/data/test.md -d {}/models/dialogue_DD/".format(self.virtual_env, 
																					self.model_path, self.model_path)
		os.chdir(self.model_path)
		os.system(cmd)