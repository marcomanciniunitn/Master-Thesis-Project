import random, re
import numpy as np

from database import Database, DONT_CARE
from actions import PollUpdates, MoreUpdates, Request as agent_Request
from customs import CustomAction, Multichoice, Propose, Lookup, CompleteTask,							\
														  TransferPreferences
from intents import Inform, Affirm, Bye, Deny, Request as user_Request,	Greet,							\
					AskMoreOptions, AskPrevOptions, AskHeadOptions, ThatsIt,							\
					DontCare

class UserProfile:

	@staticmethod
	def	get_random_profile():
		ambiguity = random.uniform(0.0, 1.0)
		indecision = random.uniform(0.0, 1.0)
		experience = random.uniform(0.0, 1.0)
		cooperation = random.uniform(0.0, 1.0)
		flexibility = random.uniform(0.0, 1.0)
		informativity_mu = random.randint(1, 3)
		informativity_sd = random.uniform(1.0, 2.0)

		return UserProfile(indecision, flexibility, experience, cooperation,
							  ambiguity, informativity_mu, informativity_sd)

	def __init__(self, indecision, flexibility, experience, cooperation, 
				 		  ambiguity, informativity_mu, informativity_sd,
				 		  	 max_ambiguous_choice=2, max_deny_propose=3,  
				 		  	 max_navigation_steps=2, max_turn_ignored=3): 

		self.ambiguous_choice_left = max_ambiguous_choice
		self.navigation_steps_left = max_navigation_steps
		self.denies_left = max_deny_propose	
		self.ignore_left = max_turn_ignored

		self.cooperation = min(max(0.0, cooperation), 1.0)
		self.flexibility = min(max(0.0, flexibility), 1.0)
		self.experience = min(max(0.0, experience), 1.0)
		self.indecision = min(max(0.0, indecision), 1.0)
		self.ambiguity = min(max(0.0, ambiguity), 1.0)
		self.informativity_mu = informativity_mu
		self.informativity_sd = informativity_sd

	def roll_for_results_navigation(self):
		if random.uniform(0, 1) > self.indecision:
			return False
		if not self.navigation_steps_left:
			return False
		self.navigation_steps_left -= 1
		return True

	def roll_for_ambiguous_choice(self):
		if random.uniform(0, 1) > self.ambiguity:
			return False
		if not self.ambiguous_choice_left:
			return False
		self.ambiguous_choice_left -= 1
		return True

	def roll_for_deny_proposal(self):
		if random.uniform(0, 1) > self.indecision:
			return False
		if not self.denies_left:
			return False
		self.denies_left -= 1
		return True

	def roll_for_cooperation(self):
		if not random.uniform(0, 1) > self.cooperation:
			return True
		if not self.ignore_left:
			return True
		self.ignore_left -= 1
		return False

	def roll_for_informativity(self):
		n = np.random.normal(self.informativity_mu, 
							 self.informativity_sd)
		return max(1, int(n))

	def roll_for_assistance(self):
		return random.uniform(0, 1) > self.experience

	def roll_for_resampling(self):
		return random.uniform(0, 1) < self.flexibility


class UserGoal:

	def __init__(self, predicate_arguments, constraints):
		self.constraints = constraints
		self.satisfied = False
		self.predicate_arguments = predicate_arguments

	def get_entity(self):
		return self.predicate_arguments['subdialog'][0]['argument']

	def update(self, last_system_action):
		pass

	def _get_values_for(self, slot):
		db = Database.get_instance()
		table_name = db.slot_to_table(slot)
		rows = db.project(table_name, {}, slot)
		return [r[slot] for r in rows]

	def resample(self, slot, exclude=[]):
		values = [v for v in self._get_values_for(slot) if v not in 									\
						  exclude + [None, self.constraints[slot]]]
		if values:
			new_value = random.choice(list(set(values)))
			self.constraints[slot] = new_value

class StepGoal(UserGoal):

	def __init__(self, predicate_arguments, constraints):
		UserGoal.__init__(self, predicate_arguments, constraints)

	def update(self, last_system_action):
		self.satisfied = last_system_action.__class__ == TransferPreferences

class EndGoal(UserGoal):

	def __init__(self, predicate_arguments, constraints):
		UserGoal.__init__(self, predicate_arguments, constraints)

	def update(self, last_system_action):
		self.satisfied = last_system_action.__class__ == CompleteTask


class UserAgenda:

	def __init__(self, goal, history):
		self.goal = goal
		self.belief = dict.fromkeys(goal.constraints, None)
		self.inform = Inform({}, self.goal.get_entity(), name="inform",
					 predicate_arguments=self.goal.predicate_arguments)

		self.history = history

	def get_unmet_constraints(self):
		belief, constr = self.belief, self.goal.constraints
		return [s for s in belief if belief[s] != constr[s]]

	def get_met_constraints(self):
		belief, constr = self.belief, self.goal.constraints
		return [s for s in belief if belief[s] == constr[s]]

	def is_goal_satisfied(self):
		return self.goal.satisfied

	def on_no_result(self, profile):
		last_inform = self.history[-1]
		last_informed_slots = list(last_inform.data.keys())
		self.belief.update({s : None for s in last_informed_slots})

		random_slot = random.choice(last_informed_slots)
		_index = last_informed_slots.index(random_slot)	
		self.goal.resample(random_slot)
		del last_informed_slots[_index]
		for slot in last_informed_slots:
			if profile.roll_for_resampling():
				self.goal.resample(slot)

	def on_multichoice(self, opts, profile):
		pool = []
		choice = random.randint(0, len(opts) - 1)
		for slot, value in opts[choice].items():
			self.goal.constraints[slot] = value
			pool.append(slot)

		for slot in pool:
			if slot not in self.goal.constraints.keys():
				msg = "user goal grown: {}".format(slot)
				self._on_error_occurred(msg)

		return self.inform_slots(pool, profile, forced=pool)

	def on_propose(self, opts, profile):
		constr = {k : v for k, v in self.goal.constraints 											\
							  .items() if v != DONT_CARE}
		suitables = []
		for opt in opts:
			if constr == {s : opt[s] for s in constr.keys()}:
				suitables.append(opt)
		
		if suitables:

			if profile.roll_for_deny_proposal(): # decline proposal
				met = self.get_met_constraints()
				if not met:
					msg = "no met constraints on propose"
					self._on_error_occurred(msg)

				rnd_constr = random.choice(met)
				self.goal.resample(rnd_constr)
				self.belief[rnd_constr] = None

			else: # user will choose one of the proposed options
				response = None
				chosen = random.choice(suitables)
				choice = opts.index(chosen) + 1
				if len(opts) == 1: # one option = yes|no question
					answer_no = hasattr(self.history[-1], "index") and 									\
								profile.roll_for_deny_proposal()  
					response = Deny() if answer_no else Affirm()
				
				elif profile.roll_for_results_navigation():
					response = random.choice([AskMoreOptions(), 
											  AskHeadOptions(), 
											  AskPrevOptions()])
				
				elif profile.roll_for_ambiguous_choice():
					n = profile.roll_for_informativity()
					n = min(n, len(chosen.keys()))
					response = self.inform.copy()
					response.is_choice()
					for i in range(n):
						k = random.choice(list(chosen.keys()))
						response.data.update({k : chosen[k]})
						del chosen[k]
				else:
					# "i want the nth option"
					response = self.inform.copy()
					response.is_choice()
					response.data['index'] = choice

				self.history.append(response)
				return response

		unmet_constraints = self.get_unmet_constraints()
		if not unmet_constraints:
			msg = ("no unmet constraints, but no valid "
				   "option among {}".format(opts))
			self._on_error_occurred(msg)

		inform = self.inform_slots(unmet_constraints, profile)
		if suitables:
			inform.is_refusal()

		return inform

	def on_request(self, slot, profile):
		response = None
		if slot in self.goal.constraints.keys():
			if isinstance(self.goal, StepGoal):
				if profile.roll_for_assistance():
					response = user_Request(slot,
						  self.goal.get_entity())
				else:
					req_slot_mentions = 0
					for turn in self.history[-2:]:
						if isinstance(turn, Inform):
							req_slot_mentions += sum([1 if s == slot else 0 for
														s in turn.data.keys()])
					if req_slot_mentions > 1:
						self.goal.constraints[slot] = DONT_CARE
						# user informed slot twice, but no result
						# so they give up and say they don't care
						self.belief[slot] = DONT_CARE
						response = DontCare()

		elif self.belief != dict.fromkeys(self.belief, None):
				response = DontCare()
		
		if response:
			self.history.append(response)
			return response

		forced = []
		if slot in self.goal.constraints.keys():
			forced.append(slot)
		
		inform = self.inform_slots(self.get_unmet_constraints(), 
							 			profile, forced=forced)
		if slot in forced:
			inform.is_reply_to_request_for(slot)

		return inform

	def on_poll_updates(self, profile):
		db = Database.get_instance()
		table = db.get_table_wname(self.goal.get_entity().split("::")[0])
		non_key_slots = [db.column_to_slot(col['column_name'], table['table_name'])						\
						 		  				 for col in table['columns'] if not 					\
						 			   				  		db.is_column_key(table, 
						 			   				  		   col['column_name'])]
		n = profile.roll_for_informativity()
		for i in range(min(len(non_key_slots), n)):
			slot_index = random.randint(0, len(non_key_slots)-1)
			to_update = non_key_slots.pop(slot_index)
			self.goal.resample(to_update)
			self.belief[to_update] = None

		return self.on_more_updates(profile)

	def on_more_updates(self, profile):
		unmet_constraints = self.get_unmet_constraints()
		if not unmet_constraints:
			self.history.append(Deny())
			return self.history[-1]

		return self.inform_slots(unmet_constraints, profile)

	def uncoop_inform(self, profile):
		pool = list(self.belief.keys())
		n = profile.roll_for_informativity()

		to_inform = []
		for i in range(min(len(pool), n)):
			slot = pool.pop(random.randint(0, len(pool)-1))
			# resample constraint for informed slot
			if slot in self.get_met_constraints():
				self.goal.resample(slot)
				self.belief[slot] = None

			to_inform.append(slot)

		inform = self.inform_slots(to_inform, profile, 
								   	 forced=to_inform)
		inform.is_uncooperative()
		return inform

	def inform_slots(self, pool, profile, forced=[]):
		inform = self.inform.copy()
		constr = self.goal.constraints
		number = profile.roll_for_informativity()
		number = min(len(pool), number) - len(forced)
		
		pool = [s for s in pool if s not in forced]
		to_inform = [s for s in forced]
		for i in range(number):
			slot_index = random.randint(0, len(pool)-1)
			to_inform.append(pool.pop(slot_index))

		for s in to_inform:
			inform.data[s]   = constr[s]
			last_value_for_s = self._last_value_for(s) 
			if last_value_for_s and constr[s] != last_value_for_s:
				inform.is_preference_change_for(s)

		self.belief.update(inform.data)
		self.history.append(inform)
		return inform

	def _last_value_for(self, slot):
		informs = [i for i in reversed(self.history) if 												\
								 isinstance(i, Inform)]
		for inform in informs:
			if slot in inform.data.keys():
				return inform.data[slot]

		return None

	def _on_error_occurred(self, error_msg):
		error_msg += ("\nconstraints: {}\nuser belief: {}"
					  "").format(self.goal.constraints,
									   	   self.belief)
		raise ValueError(error_msg)


class UserState:

	def __init__(self, goals, profile):
		self.history = []
		self.profile = profile
		self.agendas = [UserAgenda(goal, self.history) for goal in goals]

	def update_goals_state(self, turn):
		actions_with_entity = [a for a in turn if hasattr(a, 'frame') or 									\
												   hasattr(a, 'entity')]
		for a in actions_with_entity:
			entity = a.frame.entity if hasattr(a, 'frame') else a.entity
			self.get_agenda(entity).goal.update(a)

	def is_user_satisfied(self):
		full_sat = sum([agenda.is_goal_satisfied() for agenda in self.agendas])
		return full_sat == len(self.agendas)

	def get_agenda(self, entity):
		for agenda in self.agendas:
			if agenda.goal.get_entity() == entity:
				return agenda

		raise ValueError("No agenda for goal with entity: {}".format(entity))

	def update(self, turn):
		self.update_goals_state(turn)
		# random inform if cooperative roll fails, or first user turn
		# can not roll for cooperation when we are updating or closing
		can_roll_for = not [a for a in turn if isinstance(a, PollUpdates) or							\
					        	 			   isinstance(a, MoreUpdates) or 							\
					        	 			   isinstance(a, CompleteTask)]
		p = self.profile
		if not self.history or (can_roll_for and not p.roll_for_cooperation()):
			failed_lookups = [a for a in turn if isinstance(a,
								 	   Lookup) and not a.data]
			
			for failed_lookup in failed_lookups:
				entity = failed_lookup.frame.entity
				agenda = self.get_agenda(entity)
				agenda.on_no_result(p)

			agenda = random.choice(self.agendas)
			return agenda.uncoop_inform(p)

		# cooperative user reacts to system
		for action in turn:
			agenda = self.get_agenda(action.entity if hasattr(action, 'entity')							\
									 				  else action.frame.entity)

			if isinstance(action, Lookup) and not action.data:
				agenda.on_no_result(p)
			elif isinstance(action, Multichoice):
				return agenda.on_multichoice(action.data, p)
			elif isinstance(action, Propose):
				return agenda.on_propose(action.data, p)
			elif isinstance(action, agent_Request):
				return agenda.on_request(action.slot, p)
			elif isinstance(action, PollUpdates):
				return agenda.on_poll_updates(p)
			elif isinstance(action, MoreUpdates):
				return agenda.on_more_updates(p)
			elif isinstance(action, CompleteTask):
				return ThatsIt()

		error_msg = "Can not update user state for system's turn: {}"
		actions = ", ".join([action.to_string() for action in turn])
		raise ValueError(error_msg.format(actions))


class Sim:

	def __init__(self, im):
		self.state, self.im = None, im

	def prepare(self, goals, profile_feats={}):
		if not profile_feats: profile = UserProfile.get_random_profile()
		else: profile = UserProfile(profile_feats['indecision'],
							  		profile_feats['flexibility'],
							  		profile_feats['experience'],
							  		profile_feats['cooperation'],
							  		profile_feats['ambiguity'],
							  		profile_feats['informativity_mu'],
							  		profile_feats['informativity_sd'])

		self.state = UserState(goals, profile)

	def run(self):
		self.im.send_intent(Greet())
		while not self.state.is_user_satisfied():
			turn = self.im.read_actions()
			next_intent = self.state.update(turn)
			self.im.send_intent(next_intent)

		self.im.read_actions()
		self.im.send_intent(Bye())