import time
from threading import Lock
from intents import Intent
from actions import Action
from trainer import DialogManagerTrainer

class InteractionManager:

	def __init__(self, trainer):
		self.trainer = trainer
		self.actions_buff = []
		self.intent_buff = []

		# locks for multi-threading sync
		self.actions_buff_lock = Lock()
		self.intent_buff_lock = Lock()

	def send_intent(self, intent):
		self.intent_buff_lock.acquire()

		if isinstance(intent, Intent):
			self.trainer.log_intent(intent)
			self.intent_buff.append(intent)

		self.intent_buff_lock.release()

	def send_actions(self, actions):
		self.actions_buff_lock.acquire()

		actions = [a for a in actions if isinstance(a, Action)]
		self.trainer.log_actions(actions)
		self.actions_buff += actions

		self.actions_buff_lock.release()

	def read_intent(self):
		# sync wait
		while True:
			self.intent_buff_lock.acquire()

			if self.intent_buff: 
				intent = self.intent_buff.pop()
				self.intent_buff_lock.release()
				return intent

			self.intent_buff_lock.release()
			# wait for other thread to fill
			time.sleep(0.01)

	def read_actions(self):
		# sync wait
		while True:
			self.actions_buff_lock.acquire()

			if self.actions_buff:
				actions, self.actions_buff = self.actions_buff, []
				self.actions_buff_lock.release()
				return actions

			self.actions_buff_lock.release()
			# wait for other thread to fill
			time.sleep(0.01)

	def peek_intent(self):
		return self.intent_buff[-1] if self.intent_buff else None

	def peek_actions(self):
		return self.actions_buff