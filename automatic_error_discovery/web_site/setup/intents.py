import random

class Intent:

	def __init__(self):
		pass

	def __str__(self):
		return self.to_string()

	def to_string(self):
		return self.name

class DontCare(Intent):

	def __init__(self):
		self.name = "dontcare"

class ThatsIt(Intent):

	def __init__(self):
		self.name = "thatsit"

class Affirm(Intent):

	def __init__(self):
		self.name = "affirm"

class Hangup(Intent):

	def __init__(self):
		self.name = "hangup"

class Greet(Intent):

	def __init__(self):
		self.name = "greeting"

class Deny(Intent):

	def __init__(self):
		self.name = "deny"

class Bye(Intent):

	def __init__(self):
		self.name = "goodbye"

class Choose(Intent):

	def __init__(self, index):
		self.name = "choose"
		self.index = index

	def to_string(self):
		return self.name + "{" + 															\
							"\"{}\": \"{}\"".format("index", self.index) 					\
						 + "}"

class Request(Intent):

	def __init__(self, slot, entity):
		self.entity = entity
		self.name = "request"
		self.slot = slot

	def to_string(self):
		return "{}_{}".format(self.name, self.slot)

class Inform(Intent):

	def __init__(self, data, name, entity):
		self.name = name
		self.data = data
		self.entity = entity

	def copy(self):
		return Inform({k : v for k, v in self.data.items()}, 
									self.name, self.entity)

	def to_string(self):
		return self.name + "{" + 														\
						   ", ".join(["\"{}\": \"{}\"".format(k, v)						\
									for k, v in self.data.items()]) 					\
						 + "}"

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