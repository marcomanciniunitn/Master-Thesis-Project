from threading import Lock
from pathlib import Path

import yaml, datetime, re, json, copy, pickle
import tensorflow_hub as hub
import tensorflow as tf
import numpy as np

from database import Database
from agent    import ExtendedFrame
from customs  import CustomAction, Multichoice, AnswerQuestion

import intents
import actions


class DialogManagerTrainer:

	def __init__(self, frames, database, actions_file="custom_actions", 
				 domain_file="domain", stories_file="stories", timestamps=True):
		
		self.folder  = "data/"
		domain_file  = self.folder + domain_file
		actions_file = self.folder + actions_file
		stories_file = self.folder + stories_file

		timestamp = str(datetime.datetime.utcnow()).split(".")[0]
		self.domain_f = domain_file + (timestamp + ".yml" if timestamps else ".yml")
		self.stories_f = stories_file + (timestamp + ".md" if timestamps else ".md")
		self.actions_f = actions_file + (timestamp + ".py" if timestamps else ".py")
		self.file_lock = Lock()
		self.story_id = 0

		self.log_db_access(database)
		
		self.domain = {'entities' : [], 'intents' : [],
					 	  'actions' : [], 'slots' : {}, 
					 	  			  'templates' : {}}

		db = Database.get_instance()
		with open(self.actions_f, "a+") as f:
			f.write("from rasa_core.actions import Action\n\n")

		all_slots = set(sum([frame.get_all_slots() for frame in frames], []))
		tables    = set()
		for frame in frames:
			for slot in frame.get_all_slots():
				if slot not in self.domain['entities']:
					self.domain['entities'].append(slot)
					self.domain['slots'][slot] = {'type' : "text"}
					if slot in frame.get_informable_slots():
						intent = intents.Request(slot, frame.entity)
						action = actions.Request(slot, frame.entity)
						self.domain['actions'].append(action.to_string())
						self.domain['intents'].append(intent.to_string())
						self.domain['templates'][str(action)] = action.templates
						self._add_action_to_domain(Multichoice(frame,
													slot, all_slots))
			tables.add(frame.table['table_name'])
			if  isinstance(frame, ExtendedFrame):
				for slot in frame.get_requestable_slots():
					intent = intents.Question(slot, frame.entity)
					if  str(intent) not in self.domain['intents']:
						self.domain['intents'].append(str(intent))
						action = AnswerQuestion(frame, slot)
						self._add_action_to_domain(action)
		
		for frame in frames:
			# adding unfeaturized slots and entities
			unfeaturized_slots = [k for k in frame.content if k not in 									\
											  self.domain['entities']]
			self.domain['slots'].update({k : {'type' : "unfeaturized"} 									\
										 for k in unfeaturized_slots})
			self.domain['entities'].extend(unfeaturized_slots)
								
		self.domain['entities'].append("user_choice")
		self.domain['intents'].append(str(intents 														\
						.RequestBack(None, None)))

		self.domain['slots']['results_offsets']   = {'type' : "unfeaturized"}
		self.domain['slots']['results_displayed'] = {'type' : "unfeaturized"}
		self.domain['slots']['matches'] = {'type' : "unfeaturized"} # holds select query matches (saves time)
		self.domain['slots']['queries'] = {'type' : "unfeaturized"} # holds queries to be run at dialogue end
		self.domain['slots']['user_choice'] = {'type' : "text"}

		greet, bye = actions.Greet(), actions.Bye()
		self.domain['templates'][str(greet)] = greet.templates
		self.domain['templates'][str(bye)]	 = bye.templates
		self.domain['actions'].append(greet.to_string())
		self.domain['actions'].append(bye.to_string())

	def new_story_file(self, file_name, append_ts=True):
		timestamp = str(datetime.datetime.utcnow()).split(".")[0]
		self.stories_f = self.folder + file_name + (timestamp + ".md" 									\
											  if append_ts else ".md")

	def new_story(self, add_newline=False):
		with open(self.stories_f, "a+") as f:
			if add_newline:
				f.write("\n")
			f.write("## story_{}\n".format(self 														\
									.story_id))
			self.story_id += 1

	def log_intent(self, intent, verbose=False):
		self.file_lock.acquire()
		with open(self.stories_f, "a+") as f:
			f.write("* {}\n".format(intent if not verbose else 											\
									intent.to_string_verbose()))
		
		self._add_intent_to_domain(intent)
		self.file_lock.release()

	def _add_intent_to_domain(self, intent):
		seen = self.domain['intents']
		if intent.name not in seen and str(intent) not in seen:
			self.domain['intents'].append(intent.name)

	def log_actions(self, actions, verbose=False):
		self.file_lock.acquire()
		for action in actions:
			with open(self.stories_f, "a+") as f:
				f.write(" - {}\n".format(str(action) if not verbose or 									\
								  not isinstance(action, CustomAction) 									\
									 else action.to_string_verbose()))

			self._add_action_to_domain(action)
		self.file_lock.release()

	def _add_action_to_domain(self, action):
		if not isinstance(action, CustomAction):
			return

		action_name = self.actions_f[len(self.folder):-3] + "." + action.name
		if action_name not in self.domain['actions']:
			self.domain['actions'] += [action_name]
			with open(self.actions_f, "a+") as f:
				f.write(action.to_python_code())

	def build_domain_yml(self):
		with open(self.domain_f, "w") as f:
			yaml.dump(self.domain, f, default_flow_style=False)

	def log_db_access(self, database):
		db = Database.get_instance()

		self.file_lock.acquire()
		with open(self.actions_f, "a+") as f:
			f.write("from database import Database\n\n" +												\
					"Database.get_instance(database=\"" + 												\
					"{}\")\n\n".format(database))
		self.file_lock.release()


class FullAgentTrainer(DialogManagerTrainer):

	def __init__(self, frames, database, nlg_engine, 
				 actions_file="custom_actions", domain_file="domain", 
				 stories_file="stories", timestamps=True, 
				 phrases_file="nlu_training", 
				 dialogs_file="dialogs", transcript_file="transcript"):

		DialogManagerTrainer.__init__(self, frames, database,
									  actions_file=actions_file,
									  stories_file=stories_file, 
									  domain_file=domain_file,
									  timestamps=timestamps)

		transcript_file = self.folder + transcript_file
		phrases_file    = self.folder + phrases_file
		dialogs_file    = self.folder + dialogs_file

		timestamp = str(datetime.datetime.utcnow()).split(".")[0]
		self.transcript_f = transcript_file + (timestamp + ".md" if timestamps else ".md")
		self.phrases_f  = phrases_file + (timestamp + ".json" if timestamps else ".json")
		self.dialogs_f  = dialogs_file + (timestamp + ".json" if timestamps else ".json")
		self.nlg_engine = nlg_engine

	def new_story(self, add_newline=False):
		newL = Path(self.transcript_f).is_file()
		with open(self.transcript_f, "a+") as f:
			if newL:
				f.write("\n")
			f.write("## story_{}\n".format(self 														\
								  	.story_id))

		DialogManagerTrainer.new_story(self, add_newline=add_newline)

	def log_intent(self, intent, verbose=False):
		paraphrase = self.nlg_engine.intent_to_nl(intent,
								   mark_slot_values=True)
		with open(self.transcript_f, "a+") as f:
			f.write("* {}\n".format(paraphrase))

		DialogManagerTrainer.log_intent(self, intent, verbose=verbose)

	def log_actions(self, actions, verbose=False):
		with open(self.transcript_f, "a+") as f:
			f.write(" - {}\n".format(self.nlg_engine.actions_to_nl(actions)))

		DialogManagerTrainer.log_actions(self, actions, verbose=verbose)

	def build_phrases_file(self, exclude_text_only=False):
		structure = {
						'rasa_nlu_data': {
							'common_examples': [],
							'entity_examples': [],
							'intent_examples': []
						}
					}

		utterance_template = {'text': None, 'intent': None, 'entities': []}
		entity_template    = {'start': None, 'end'   : None,
							  'value': None, 'entity': None}
		
		seen = set()

		with open(self.transcript_f, "r") as f:
			for line in f.read().split("\n"):
				if not line:
					continue
				if not line[0] == "*":
					continue

				regex = ("<intent name=\"[^\"]+\">(.+)"
						 "</intent name=\"([^\"]+)\">")

				utterance = re.search(regex, line).group(1)
				intent    = re.search(regex, line).group(2)
				entities  = []

				regex = ("(<entity name=\"[^\"]+\" value="
						 "\"[^\"]+\">([^<]+)</entity name"
						 "=\"[^\"]+\" value=\"[^\"]+\">).*")

				while re.search(regex, utterance):
					matches = re.search(regex, utterance)
					_rex = ("<entity name=\"([^\"]+)\" value=\"([^\"]+)\">.*")
					_cpy = entity_template.copy()

					_cpy['entity'] = re.search(_rex, matches.group(1)).group(1)
					_cpy['value']  = re.search(_rex, matches.group(1)).group(2)
					_cpy['start']  = utterance.find(matches.group(1))
					_cpy['end']    = _cpy['start'] + len(matches.group(2))

					utterance      = utterance.replace(matches.group(1), 
													   matches.group(2))
					entities.append(_cpy)

				if not entities and exclude_text_only:
					continue

				_cpy = copy.deepcopy(utterance_template)
				_cpy['text']	 = utterance
				_cpy['intent']   = intent
				_cpy['entities'] = entities

				if _cpy['text'] not in seen:
					structure['rasa_nlu_data']['common_examples'].append(_cpy)
					seen.add(_cpy['text'])

		with open(self.phrases_f, "a+") as f:
			json.dump(structure, f, indent=4, ensure_ascii=False)

	def build_file_for_hit(self):
		structure 		= {'dialogs': []}
		dialog_template = {'id': None, 'turns': []}
		entity_template = {'start': None, 'end' : None, 
						   'value': None, 'name': None}
		turn_template   = {
			'number': None,
			'agent': {
				'text': None
			},
			'user': {
				'text': None,
				'intent': None,
				'entities': []
			},
			'turk': {
				'paraphrases': []
			}
		}

		dialog, turn, next_turn = None, None, None
		with open(self.transcript_f, "r") as f:
			for line in f.read().split("\n"):
				if not line:
					continue
				
				if line[0] == "#":
					dialog = copy.deepcopy(dialog_template)
					structure['dialogs'].append(dialog)
					dialog['id'] = line.split("_")[1]
					next_turn, turn = 0, None
				
				elif line[0] == " ":
					utterance = line[3:]
					turn = copy.deepcopy(turn_template)
					turn['number']        = next_turn
					turn['agent']['text'] = utterance
					dialog['turns'].append(turn)
					next_turn += 1
					
					assert dialog is not None

				# skips first user turn
				elif line[0] == "*" and turn:
					regex = ("<intent name=\"[^\"]+\">(.+)"
							 "</intent name=\"([^\"]+)\">")
					utterance = re.search(regex, line).group(1)
					intent    = re.search(regex, line).group(2)

					regex = ("(<entity name=\"[^\"]+\" value="
							 "\"[^\"]+\">([^<]+)</entity name"
							 "=\"[^\"]+\" value=\"[^\"]+\">).*")

					assert dialog is not None

					while re.search(regex, utterance):
						matches = re.search(regex, utterance)
						_rex = ("<entity name=\"([^\"]+)\" value=\"([^\"]+)\">.*")
						_cpy = entity_template.copy()
						_cpy['name']  = re.search(_rex, matches.group(1)).group(1)
						_cpy['value'] = re.search(_rex, matches.group(1)).group(2)
						_cpy['start'] = utterance.find(matches.group(1))
						_cpy['end']	  = _cpy['start'] + len(matches.group(2))
						
						turn['user']['entities'].append(_cpy)
						utterance = utterance.replace(matches.group(1), 
													  matches.group(2))
						
					turn['user']['text']   = utterance
					turn['user']['intent'] = intent
					turn = None

		with open(self.dialogs_f, "a+") as f:
			json.dump(structure, f, indent=4, ensure_ascii=False)

	def build_raw_transcript(self):
		file = self.folder + "raw_" + self.transcript_f[len(self.folder):]
		
		with open(self.transcript_f, "r") as f:
			with open(file, "a+") as g:
				
				for line in f.read().split("\n"):
					regex = ("(<intent name=\"[^\"]+\">(.+)"
						 	 "</intent name=\"[^\"]+\">)")
					
					matches = re.search(regex, line)
					if matches:
						line = line.replace(matches.group(1),
											matches.group(2))

					regex = ("(<entity name=\"[^\"]+\" value="
							 "\"[^\"]+\">([^<]+)</entity name"
							 "=\"[^\"]+\" value=\"[^\"]+\">).*")

					while re.search(regex, line):
						matches = re.search(regex, line)
						line = line.replace(matches.group(1), 
											matches.group(2))
					g.write(line + "\n")


class Seq2ActionAgentTrainer(FullAgentTrainer):

	def __init__(self, frames, database, nlg_engine,
				 actions_file="custom_actions", domain_file="domain", 
				 stories_file="stories", timestamps=True, 
				 phrases_file="nlu_training",  dialogs_file="dialogs",
				 transcript_file="transcript", embeddings_file="embeddings",
				 		  					  		lexicon_file="lexicon"):

		FullAgentTrainer.__init__(self, frames, database, nlg_engine,
				  actions_file=actions_file, domain_file=domain_file,  
				  stories_file=stories_file, timestamps=timestamps, 
				  phrases_file=phrases_file, 
				  dialogs_file=dialogs_file,
				  transcript_file=transcript_file)

		embeddings_file = self.folder + embeddings_file
		lexicon_file    = self.folder + lexicon_file

		timestamp = str(datetime.datetime.utcnow()).split(".")[0]
		self.embeddings_f = embeddings_file + (timestamp if timestamps else "") + ".pickle"
		self.lexicon_f    = lexicon_file + (timestamp if timestamps else "") + ".txt"

		self.domain['entities'].append("text")
		self.domain['intents'] = ["communicate"]
		self.domain['slots']['text'] = {'type' : "text"}

	def log_intent(self, intent, verbose=False):
		paraphrase = self.nlg_engine.intent_to_nl(intent,
								   mark_slot_values=True)
		# change intent name to "communicate"
		regex = ("<intent name=\"[^\"]+\">(.+)</intent name=\"[^\"]+\">")
		paraphrase = ("<intent name=\"communicate\">{}</intent name=\""
					  "communicate\">".format(re.search(regex,
					  					paraphrase).group(1)))

		with open(self.transcript_f, "a+") as f:
			f.write("* {}\n".format(paraphrase))
		
		if isinstance(intent, intents.Inform):
			data = intent.data
		else:
			data = {}

		# remove intent tag from text
		regex = ("<intent name=\"[^\"]+\">(.+)"
				 "</intent name=\"[^\"]+\">")
		paraphrase = re.search(regex, 
				 paraphrase).group(1)

		# remove all entities' tags from text
		regex = ("(<entity name=\"[^\"]+\" value="
				 "\"[^\"]+\">([^<]+)</entity name"
				 "=\"[^\"]+\" value=\"[^\"]+\">).*")
		
		while re.search(regex, paraphrase):
			matches    = re.search(regex, paraphrase)
			paraphrase = paraphrase.replace(matches.group(1),
											matches.group(2))
		# create new "communicate" intent
		intent = intents.Communicate(paraphrase, data)
		DialogManagerTrainer.log_intent(self, intent, 
									 verbose=verbose)

	def build_user_lexicon(self):
		lexicon = set()
		for sentence in self._get_user_sentences():
			for token in sentence.split(" "):
				lexicon.add(token)

		with open(self.lexicon_f, "a+") as f:
			for token in lexicon:
				f.write(token)
				f.write("\n")

	def build_phrases_file(self, exclude_text_only=False):
		FullAgentTrainer.build_phrases_file(self, exclude_text_only=True)

	def compute_sentence_embeddings(self, algorithm="elmo"):
		if   algorithm == "elmo":
			e = self._compute_elmo_embeddings()
		elif algorithm == "usem":
			e = self._compute_usem_embeddings()
		else:
			print("[!] '{}' is not a valid algorithm for "
				  "sentence embeddings".format(algorithm))
			return

		pickle.dump(e, open(self.embeddings_f, "wb"))

	def _compute_elmo_embeddings(self):
		elmo    = hub.Module("https://tfhub.dev/google/elmo/2")
		init    = tf.global_variables_initializer()
		session = tf.Session()
		session.run(init)

		sentences  = [sentence for sentence in self 													\
							._get_user_sentences()]

		print("[...] computing elmo embeddings...")
		embeddings = elmo(sentences, signature="default",
					 				as_dict=True)['elmo'] 												\
								   .eval(session=session)

		elmo_embeddings = {}
		for i, embedding in enumerate(embeddings):
			embedding = np.average(embedding, axis=0).tolist()
			elmo_embeddings[sentences[i]] = embedding

		return elmo_embeddings

	def _compute_usem_embeddings(self):
		usem 	= hub.Module("https://tfhub.dev/google/universal-"
							 "sentence-encoder/2")
		init 	= tf.global_variables_initializer()
		session = tf.Session()
		session.run(init)
		session.run(tf.tables_initializer())

		sentences = [sentence for sentence in self 														\
							._get_user_sentences()]

		print("[...] computing universal sentence encoder embeddings...")
		embeddings = usem(sentences).eval(session=session)

		usem_embeddings = {}
		for i, embedding in enumerate(embeddings):
			usem_embeddings[sentences[i]] = embedding
		
		return usem_embeddings

	def _get_user_sentences(self):
		sentences = set()
		with open(self.transcript_f, "r") as f:
			for line in f.read().split("\n"):
				if not line:
					continue
				if line[0] != "*":
					continue

				regex = ("<intent name=\"[^\"]+\">(.+)"
						 "</intent name=\"[^\"]+\">")
				
				utterance = re.search(regex, line).group(1)
				
				regex = ("(<entity name=\"[^\"]+\" value="
				 		 "\"[^\"]+\">([^<]+)</entity name"
				 		 "=\"[^\"]+\" value=\"[^\"]+\">).*")

				while re.search(regex, utterance):
					matches = re.search(regex, utterance)
					utterance = utterance.replace(matches.group(1),
												  matches.group(2))
				sentences.add(utterance)

		return sentences