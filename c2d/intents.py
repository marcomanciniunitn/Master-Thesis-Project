import random

def clean(v):
	if isinstance(v, str):
		return v.replace('"', r'\"')

	return v

class Intent:

	def __init__(self):
		pass

	def __str__(self):
		return self.to_string()

	def to_string(self):
		return self.name

	def to_string_verbose(self):
		return self.to_string()

	def get_full_name(self):
		return self.name

class ThatsIt(Intent):

	def __init__(self):
		self.name = "thatsit"

class Affirm(Intent):

	def __init__(self):
		self.name = "affirm"

class Repeat(Intent):

	def __init__(self):
		self.name = "ask_to_repeat"

class GiveUp(Intent):

	def __init__(self):
		self.name = "giveup"

class Greet(Intent):

	def __init__(self):
		self.name = "greeting"

class Deny(Intent):

	def __init__(self):
		self.name = "deny"

class Bye(Intent):

	def __init__(self):
		self.name = "goodbye"

class DontCare(Intent):

	def __init__(self):
		self.name = "dontcare"

class Question(Intent):

	def __init__(self, slot, entity, data={}):
		self.entity = entity
		self.name = "ask"
		self.slot = slot
		self.data = data

		self.context = {}

	def to_string(self):
		return "{}_{}".format(self.name,  self.slot)													\
				+ ("{" + ", ".join([("\"{}\": \"{}\""													\
				"").format(k, clean(v)) for k, v in 													\
				self.data.items()]) + "}" if self.data else "")

	def get_full_name(self):
		return self.name + "_{}".format(self.slot)

class Request(Intent):

	def __init__(self, slot, entity, data={}):
		self.entity = entity
		self.name = "request"
		self.slot = slot
		self.data = data

		self.context = {
			'user_is_being_uncooperative' : False
		}

	def to_string(self):
		return "{}_{}".format(self.name,  self.slot)													\
				+ ("{" + ", ".join([("\"{}\": \"{}\""													\
				"").format(k, clean(v)) for k, v in 													\
				self.data.items()]) + "}" if self.data else "")

	def to_string_verbose(self):
		return self.to_string() + "_{}".format(["{}: {}".format(k, v)									\
								  for k, v in self.context.items() if 									\
								  v is not None])

	def get_full_name(self):
		return self.name + "_{}".format(self.slot)

	def is_uncooperative(self):
		self.context['user_is_being_uncooperative'] = True

class RequestBack(Intent):

	def __init__(self, slot, entity):
		"""
			user returns the request to the system:
			u: which color do you want?
			s: which ones do you have?
		"""
		self.entity = entity
		self.name = "request_back"
		self.slot = slot

class Inform(Intent):

	def __init__(self, data, entity, name="inform", predicate_arguments=[]):
		self.name = name # todo: use predicate argument at subdialog level
		self.data = data
		self.entity = entity

		self.predicate_arguments = predicate_arguments	# used by nlg
		self.context = 	{								# used by nlg
			'user_is_changing_preference_for' : [],
			'user_is_replying_to_request_for' : [],
			'user_is_choosing_multichoice': False,
			'user_is_being_uncooperative' : False,
			'user_is_declining_proposal'  : False,
			'user_is_choosing_proposal'   : False,
			'user_is_opening'  : False
		}

	def copy(self):
		return Inform({k : v for k, v in self.data.items()},
					   			self.entity, name=self.name, 
									predicate_arguments=self											\
					   				   .predicate_arguments)

	def to_string(self):
		return self.name + "{" + 																		\
						   ", ".join(["\"{}\": \"{}\"".format(k, clean(v))								\
										   for k, v in self.data.items()]) 								\
						 + "}"

	def to_string_verbose(self):
		return self.to_string() + "_{}".format(["{}: {}".format(k, v)									\
							  for k, v in self.context.items()  if v 									\
							  is not None])

	# methods for updating context - context is needed for nlg

	def is_preference_change_for(self, slot):
		self.context['user_is_changing_preference_for'].append(slot)

	def is_reply_to_request_for(self, slot):
		self.context['user_is_replying_to_request_for'].append(slot)

	def is_uncooperative(self):
		self.context['user_is_being_uncooperative'] = True

	def is_multichoice(self):
		self.context['user_is_choosing_multichoice'] = True

	def is_refusal(self):
		self.context['user_is_declining_proposal']  = True

	def is_choice(self):
		self.context['user_is_choosing_proposal'] = True

	def is_opener(self):
		self.context['user_is_opening'] = True
		

# intents for result list navigation

class AskMoreOptions(Intent):

	def __init__(self):
		self.name = "ask_more_options"

class AskPrevOptions(Intent):

	def __init__(self):
		self.name = "ask_prev_options"

class AskHeadOptions(Intent):

	def __init__(self):
		self.name = "ask_head_options"

# intent for natural language

class Communicate(Intent):

	def __init__(self, text, data):
		self.name = "communicate"
		self.text = text
		self.data = data

	def to_string(self):
		data = {k : v for k, v in self.data.items()}
		data['text'] = self.text
		return self.name + "{" +																		\
						   ", ".join(["\"{}\": \"{}\"".format(k, clean(v))								\
						   				 		for k, v in data.items()])								\
						 + "}"