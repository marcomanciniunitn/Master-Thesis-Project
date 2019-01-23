from database import Database
from customs import CustomAction
from intents import ThatsIt, Affirm, Greet, Deny, Bye, DontCare,										\
					Request, Inform, AskMoreOptions, AskPrevOptions,									\
					AskHeadOptions, Question, GiveUp, Repeat, RequestBack

import numpy as np
import random, nltk
from nltk.corpus import wordnet as wn

class RuleBasedEngine:

	def __init__(self):

		self.int_to_ordinal  = {
			1 : ["first", "1st", "1st option", "option 1", "first one", "number one"],
			2 : ["second", "2nd", "2nd option", "option 2", "second one", "number two"],
			3 : ["third", "3rd", "3rd option", "option 3", "third one", "number three",
				 "last", "last one"]
		}

		self.auxiliary_verbs = ["i want to ", "i would like to ",
								"i wanted to ", "i need to ", "",
								"", "i would prefer to ", "", ""]

		self.request_verbs   = ["i want you to ", "i need you to ",
								"can you ", "you have to ", "", ""]
		
		self.base_predicates = {
			'insert' : ["make", "add", "insert", "register"],
			'update' : ["modify", "update", "change"],
			'delete' : ["cancel", "delete", "remove"],
			'select' : ["look for", "search", "find"]
		}

		self.intent_dictionary = {
			AskMoreOptions  : ["show me more options"],
			AskPrevOptions	: ["show me the previous options"],
			AskHeadOptions	: ["show me the first options"],
			DontCare 		: ["i don't have a preference", "anything will do"],
			ThatsIt			: ["that is it", "that's it thank you"],
			Affirm 			: ["yes", "sure", "yes please", "yes thank you"],
			GiveUp			: ["you don't have what i was looking for, goo"
							   "dbye", "i can't find what i needed, bye"],
			Repeat			: ["can you repeat that please?", "come again?",
							   "say that again?"],
			Greet 			: ["hello", "hi there"],
			Deny			: ["no"],
			Bye				: ["goodbye", "bye"],
		}

	def actions_to_nl(self, actions):
		return " ".join([(action.to_natural_language() if isinstance(action,
						 CustomAction) else random.choice(action.templates)) 							\
						.lower() for action in actions]).replace("  ", " ") 							\
						.strip().lstrip()

	def intent_to_nl(self, intent, mark_slot_values=False):
		if isinstance(intent, Question):
			utterance = self._phrase_user_question(intent,
				 		mark_slot_values=mark_slot_values)
		elif isinstance(intent, Inform):
			utterance = self._phrase_user_inform(intent,
				 	  mark_slot_values=mark_slot_values)
		elif isinstance(intent, Request):
			utterance = self._phrase_user_request(intent,
					   mark_slot_values=mark_slot_values)
		elif isinstance(intent, RequestBack):
			utterance = self._phrase_user_request(intent,
					   mark_slot_values=mark_slot_values,
									  use_anaphorae=True)
		else:
			utterance = random.choice(self.intent_dictionary 											\
										 [intent.__class__])

		return "<intent name=\"{i}\">{c}</intent name=\"{i}\">" 										\
				.format(i=intent.get_full_name(), c=utterance)

	def _phrase_user_question(self, intent, mark_slot_values=False):
		openers = ["can you", "could you", ""]
		verbs   = ["give me", "tell me"]

		requested = Database.get_instance().slot_to_column(intent.slot)
		phrase = random.choice(openers) + " " + random.choice(verbs)
		phrased_slots = self._phrase_informed_slots(intent, 
						mark_slot_values=mark_slot_values)
		
		phrase = phrase.lstrip()

		if 'index' in intent.data.keys():
			phrase += random.choice([" the {} of the {}".format(requested, 
					  phrased_slots), " the {}'s {}".format(phrased_slots,
					  requested)])
		elif intent.data:
			e       = intent.entity
			phrase += random.choice([" the {} of the one with {}"
					 .format(requested, phrased_slots), " the {}"
					  " of the {} having {}".format(requested, e,
					  phrased_slots)])
		else:
			phrase += " its {}".format(requested)

		return phrase + random.choice([" please", " thanks"])

	def _phrase_user_request(self, intent, mark_slot_values=False, 
											  use_anaphorae=False):
		if use_anaphorae:
			utterances = ["show me a list of options", "help me choose one?",
						  								   "any suggestion?"]
			return random.choice(utterances)

		slot 	= intent.slot
		table 	= Database.get_instance().slot_to_table(slot)
		column 	= Database.get_instance().slot_to_column(slot)

		if intent.data and intent.context['user_is_being_uncooperative']:
			utterances = ["which {t}'s {pc} do you have with",  "show me {pc}"
						  " for {pt} having", "which {pc} are there for {pt}"
						  " that have", "can you give me the available {t}'s"
						  " {pc} with"]

			phrase = random.choice(utterances).format(c=column, t=table,
					 pc=self.__to_plural(column), pt=self.__to_plural(table)) 							\
					.replace("_", " ") + " " + self._phrase_informed_slots(intent,
					 		  					mark_slot_values=mark_slot_values)

		elif intent.context['user_is_being_uncooperative']:
			utterances = ["which {t}'s {pc} are there?", "any sugges"
						  "tion for {a} {t}'s {c}?", "can you show m"
						  "e the available {pt}' {pc}?"]
			
			phrase = random.choice(utterances).format(c=column, t=table,
			 a=random.choice(["the", "a"]), pc=self.__to_plural(column), 
			 pt=self.__to_plural(table)).replace("_", " ")

		else:
			utterances = ["which {}'s {} are there?".format(table, 
						  self.__to_plural(column)), "can you sho"
						  "w me the available {}?".format(column)]

			phrase = random.choice(utterances).replace("_", " ")

		return phrase

	def _phrase_user_inform(self, inform, mark_slot_values=False):
		if inform.context['user_is_being_uncooperative']:
			return self._phrase_uncoop_user_inform(inform,
						mark_slot_values=mark_slot_values)
		else:
			return self._phrase_coop_user_inform(inform,
					  mark_slot_values=mark_slot_values)

	def _phrase_uncoop_user_inform(self, inform, mark_slot_values=False):
		if inform.context['user_is_opening'] or random.uniform(0,1) > .8:
			return self._dialog_level_inform_phrasing(inform, 
						   mark_slot_values=mark_slot_values)
		else:
			return self._subdialog_level_inform_phrasing(inform,
							  mark_slot_values=mark_slot_values)

	def _phrase_coop_user_inform(self, inform, mark_slot_values=False):
		is_choice = inform.context['user_is_choosing_proposal'] or 										\
					inform.context['user_is_choosing_multichoice']
		if is_choice:
			verb = random.choice(["i want ", "i prefer ", "give me ",
								  "i'll have ", "i'll go with ", ""])
			is_ambiguous = inform.context['user_is_choosing_proposal'] 									\
						   and 'index' not in inform.data.keys()
			if is_ambiguous:
				pronoun  = random.choice(["that one ", "the one "])
				verb    += pronoun + "with "
			
			return verb + self._phrase_informed_slots(inform,
						   mark_slot_values=mark_slot_values)
			
		informed_slots = list(inform.data.keys())
		if inform.context['user_is_replying_to_request_for'] == informed_slots:
			phrase = ""
			if inform.context['user_is_changing_preference_for']:
				# fully cooperative with goal change, reinforming slot
				phrase += random.choice(["i see. ", "oh ok. ", "alright. "])
				phrase += random.choice(["what about ", "and do you have "])
				phrase += self._phrase_informed_slots(inform,
						   mark_slot_values=mark_slot_values)
				phrase += random.choice([" then", ""])
			else:
				# fully cooperative, no goal change, single slot inform
				phrase += random.choice(self.auxiliary_verbs)[:-3]
				phrase += self._phrase_informed_slots(inform,
						   mark_slot_values=mark_slot_values)
				phrase += random.choice([" thanks", " please", ""])

			return phrase
		
		else:
			# user is replying to system request but it's overinformative
			if random.uniform(0, 1) > .5:
				phrase  = random.choice(self.auxiliary_verbs)[:-3]
				phrase += self._phrase_informed_slots(inform,
						   mark_slot_values=mark_slot_values)
				phrase += random.choice([" thanks", " please", ""])
			else:
				phrase  = self._subdialog_level_inform_phrasing(inform,
									mark_slot_values=mark_slot_values)
			return phrase

	def _subdialog_level_inform_phrasing(self, inform, mark_slot_values=False):
		predicate_argument = self._pick_predicate_argument(inform 										\
								.predicate_arguments['subdialog'],
													baseline=False)
		predicate = predicate_argument['predicate']
		argument  = predicate_argument['argument']
		is_subdialog = inform.predicate_arguments['subdialog']											\
								  [0]['predicate'] == 'select'
		
		return self._build_inform_utterance(inform, predicate, argument,
				 False, is_subdialog, mark_slot_values=mark_slot_values)

	def _dialog_level_inform_phrasing(self, inform, mark_slot_values=False):
		predicate_argument = self._pick_predicate_argument(inform 										\
								   .predicate_arguments['dialog'],
													baseline=False)
		predicate = predicate_argument['predicate']
		argument  = predicate_argument['argument']
		is_subdialog = inform.predicate_arguments['subdialog']											\
								  [0]['predicate'] == 'select'
		
		return self._build_inform_utterance(inform, predicate, argument,
				  True, is_subdialog, mark_slot_values=mark_slot_values)

	def _build_inform_utterance(self,  inform,  predicate,  argument,
								phrased_at_dialog_level, is_subdialog,
								mark_slot_values=False):
		phrase = ""
		if inform.context['user_is_declining_proposal']:
			phrase += random.choice(["no. ", "that won't do it. "])
		if inform.context['user_is_changing_preference_for']:
			phrase += random.choice(["on second thought, ", "actually, ", ""])

		phrase += random.choice(self.auxiliary_verbs + self.request_verbs)
		phrase += predicate + " "

		argument = argument.replace("_", " ")
		phrased_slot_informs = self._phrase_informed_slots(inform,
								mark_slot_values=mark_slot_values) + " "
		options = []
		if not is_subdialog:
			argument = "a {}".format(argument)
			options.append(argument + " for " + phrased_slot_informs)
			options.append(argument + ". " + phrased_slot_informs)
		
		elif phrased_at_dialog_level:
			e 		 = inform.entity
			argument = "a {}".format(argument)
			aux_verb = random.choice(self.auxiliary_verbs)[:-4]
			options.append(argument + ". {} {} with ".format(aux_verb, 
						  self.__to_plural(e)) + phrased_slot_informs)
			options.append(argument + " for {} having ".format(self 									\
							.__to_plural(e)) + phrased_slot_informs)
		else:
			plural_argument = self.__to_plural(argument)
			options.append(phrased_slot_informs + plural_argument + " ")
			options.append(plural_argument + " with " + phrased_slot_informs)
		
		phrase += random.choice(options).strip() + " "
		phrase += random.choice(["thanks", "please", ""])

		return phrase.replace("  ", " ").strip()

	def _pick_predicate_argument(self, predicate_arguments, baseline=True,
														use_wordnet=False):
		to_pick   = 0 if baseline else random.randint(1, 
						  len(predicate_arguments)) - 1
		
		argument  = predicate_arguments[to_pick]['argument']
		predicate = predicate_arguments[to_pick]['predicate']
		if predicate in self.base_predicates.keys():
			predicates = self.base_predicates[predicate]
			predicate  = random.choice(predicates)

		if use_wordnet:
			# use wordnet to find new predicate-argument structures
			argument   = self.__get_synonym_for_noun(argument)
			predicate  = self.__get_synonym_for_verb(predicate)
		
		return {'predicate' : predicate, 'argument' : argument}

	def _phrase_informed_slots(self, inform, use_wordnet=False, 
										mark_slot_values=False,
										  corrupt_values=False):
		
		opening_tag = "<entity name=\"{s}\" value=\"{w}\">"
		closing_tag = "</entity name=\"{s}\" value=\"{w}\">"

		if 'index' in inform.data.keys():
				i 			= inform.data['index']
				user_choice = random.choice(self.int_to_ordinal[i])
				return (opening_tag.format(s="user_choice", w=i) if 									\
						mark_slot_values else "") +  user_choice  + 									\
					   (closing_tag.format(s="user_choice", w=i) if 									\
						mark_slot_values else "")

		conjunction 		 = random.choice([" and ", " ", ", "])
		preference_phrasings = ["{k} {v}", "{v} {k}", "{v}",
								"{v} {k}", "{k} {v}"]
		if mark_slot_values:
			preference_phrasings = [pp.replace("{v}", "{}".format(opening_tag) 							\
									+ "{v}" + "{}".format(closing_tag)) for pp 							\
									in preference_phrasings]

		if not isinstance(inform, Inform) or inform.context['user_is_choosing_proposal']:
			del preference_phrasings[2]

		changes = inform.context.get('user_is_changing_preference_for', [])

		db = Database.get_instance()
		if use_wordnet:
			# use wordnet for column names, not for values
			return conjunction.join([random.choice(preference_phrasings) 								\
					.format(k=self.__get_synonym_for_noun(db.slot_to_column(k))							\
					.replace("_", r" "), v=(self.__corrupt(v) if corrupt_values 						\
					else v), s=k, w=v) + (" instead" if k in changes else "") 							\
					for k, v in inform.data.items()])
		else:
			return conjunction.join([random.choice(preference_phrasings) 								\
					.format(k=db.slot_to_column(k).replace("_", r" "), 
					v=(v  if not corrupt_values else self.__corrupt(v,
					use_wordnet=False)), s=k, w=v) + (" instead" if k 									\
					in changes else "") for k, 
					v in inform.data.items()])

	def __get_synsets_distribution_for_verb(self, verb):
		return self.__get_synsets_distribution_for_word(verb, pos=wn.VERB)

	def __get_synsets_distribution_for_noun(self, noun):
		return self.__get_synsets_distribution_for_word(str(noun))

	def __get_synsets_distribution_for_word(self, word, pos=wn.NOUN, 
														cutoff=0.1):
		N = 1.0 * sum([lemma.count() for synset in wn.synsets(word,
							pos=pos) for lemma in synset.lemmas()])
		if N == 0:
			return {word : 1.0}

		synonyms_counter = {}
		for synset in wn.synsets(word, pos=pos):
			for lemma in synset.lemmas():
				name  = lemma.name()
				count = lemma.count()

				if name in synonyms_counter.keys():
					synonyms_counter[name] += count
				else:
					synonyms_counter[name]  = count
	
		# apply smoothing
		synonyms_counter = {k : (0 if v / N < cutoff else v) for k,
		 							 v in synonyms_counter.items()}
		
		N = 1.0 * sum(list(synonyms_counter.values()))
		if N == 0:
			return {word : 1.0}

		return {k : v / N for k, v in synonyms_counter.items() if v > 0}

	def __get_synonym_for_noun(self, noun):
		distribution  = self.__get_synsets_distribution_for_noun(noun)
		return np.random.choice(list(distribution.keys()),
		 				   p=list(distribution.values()))

	def __get_synonym_for_verb(self, verb):
		distribution  = self.__get_synsets_distribution_for_verb(verb)
		return np.random.choice(list(distribution.keys()),
		 				   p=list(distribution.values()))

	def __to_plural(self, word):
		if word[-1] == 's': # might be already plural...
			return random.choice([word, word + "es"])
		if word[-1] in ['s', 'x', 'z'] or word[-2:] in ['sh', 'ch']:
			return word + "es"
		elif word[-1] == 'y' and word[-2] not in ['a', 'e', 'i', 'o', 'u']:
			return word[:-1] + "ies"
		else:
			return word + "s"

	def __corrupt(self, value, use_wordnet=False):
		if use_wordnet:
			value = " ".join([self.__get_synonym_for_noun(noun)  										\
							   		for noun in value.split()])
		if len(value.split()) > 1:
			corrupted = []
			value 	  = value.split()
			keep  	  = random.randint(1, len(value))
			
			for i in range(keep):
				take = random.randint(1, len(value)) - 1
				corrupted.append(value[take])
				del value[take]

			value = " ".join(corrupted)

		return value