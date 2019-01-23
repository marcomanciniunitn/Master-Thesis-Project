import random, re
import numpy as np

from database import Database, DONT_CARE
from actions import PollUpdates, MoreUpdates, Request as agent_Request
from customs import CustomAction, Multichoice, Propose, Lookup, CompleteTask,							\
					TransferPreferences, RepeatLastTurn
from intents import Inform, Affirm, Bye, Deny, Request as user_Request,	Greet,							\
					AskMoreOptions, AskPrevOptions, AskHeadOptions, ThatsIt,							\
					DontCare, GiveUp, Question, Repeat, RequestBack

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
						  giveup_probability=0.1, ichannel_quality=0.99,
						  ochannel_quality=0.99, max_ambiguous_choice=2, 
						  max_deny_propose=1, max_navigation_steps=2, 
						  max_turn_ignored=1, max_questions=2): 

		self.ambiguous_choice_left = max_ambiguous_choice
		self.navigation_steps_left = max_navigation_steps
		self.ignores_left 	  = max_turn_ignored
		self.denies_left 	  = max_deny_propose
		self.questions_left   = max_questions

		self.cooperation = min(max(0.0, cooperation), 1.0)
		self.flexibility = min(max(0.0, flexibility), 1.0)
		self.experience  = min(max(0.0, experience), 1.0)
		self.indecision  = min(max(0.0, indecision), 1.0)
		self.ambiguity   = min(max(0.0, ambiguity), 1.0)
		self.informativity_mu = informativity_mu
		self.informativity_sd = informativity_sd

		self.giveup_probability = giveup_probability
		self.ichannel_quality   = ichannel_quality
		self.ochannel_quality   = ochannel_quality

	def roll_for_cooperation(self):
		coins  = [self.ignores_left]
		result = self._roll(not random.uniform(0, 1) > self 											\
						   .cooperation, True, coins=coins)
		self.ignores_left = coins[0]
		return result

	def roll_for_ask_question(self):
		coins  = [self.questions_left]
		result = self._roll(not random.uniform(0, 1) > self 											\
						   .experience, False, coins=coins)
		self.questions_left = coins[0]
		return result

	def roll_for_deny_proposal(self):
		coins  = [self.denies_left]
		result = self._roll(random.uniform(0, 1) > self 												\
					   .indecision, False, coins=coins)
		self.denies_left = coins[0]
		return result

	def roll_for_results_navigation(self):
		coins  = [self.navigation_steps_left]
		result = self._roll(random.uniform(0, 1) > self 												\
					   .indecision, False, coins=coins)
		self.navigation_steps_left = coins[0]
		return result

	def roll_for_ambiguous_choice(self):
		coins  = [self.ambiguous_choice_left]
		return self._roll(random.uniform(0, 1) > self 													\
					  .ambiguity, False, coins=coins)
		self.ambiguous_choice_left = coins[0]
		return result

	def roll_for_informativity(self):
		n = np.random.normal(self.informativity_mu, 
							 self.informativity_sd)
		return max(1, int(n))

	def roll_for_giveup(self):
		return random.uniform(0, 1) < self.giveup_probability

	def roll_for_assistance(self):
		return random.uniform(0, 1) > self.experience

	def roll_for_resampling(self):
		return random.uniform(0, 1) < self.flexibility

	def roll_for_input_corrupt(self):
		return random.uniform(0, 1) > self.ichannel_quality

	def roll_for_output_corrupt(self):
		return random.uniform(0, 1) > self.ochannel_quality

	def _roll(self, condition, if_condition, coins=[]):
		if condition or (coins and not coins[0]):
			return if_condition

		coins[0] -= 1
		return not if_condition

class UserGoal:

	def __init__(self, predicate_arguments, constraints, requestables):
		self.requestables = requestables
		self.constraints  = constraints 
		self.satisfied    = False
		self.predicate_arguments = predicate_arguments

	def get_entity(self):
		return self.predicate_arguments['subdialog'][0]['argument']

	def update(self, last_system_action):
		pass

	def _get_values_for(self, slot, conditioned_on={}):
		db 		   = Database.get_instance()
		table_name = db.slot_to_table(slot)
		
		values = []
		if conditioned_on:
			rows   = db.kb_lookup(table_name, conditioned_on)
			values = list(set([r[slot] for r in rows]))
		if not values:
			rows   = db.project(table_name, {}, slot)
			values = [r[slot] for r in rows]
		
		return values

	def resample(self, slot, exclude=[], conditioned_on={}):
		if slot not in self.constraints.keys():
			error_msg  = "user goal does not have: {}".format(slot)
			error_msg += "\nuser goal: {}".format(self.constraints)
			raise ValueError(error_msg)

		values = [v for v in self._get_values_for(slot, 
				 conditioned_on=conditioned_on) if v not in 											\
				 exclude +  [None, self.constraints[slot]]]
		
		if values:
			new_value = random.choice(list(set(values)))
			self.constraints[slot] = new_value

class StepGoal(UserGoal):

	def __init__(self, predicate_arguments, constraints, requestables):
		UserGoal.__init__(self, predicate_arguments, constraints, requestables)

	def update(self, last_system_action):
		self.satisfied = last_system_action.__class__ == TransferPreferences

class EndGoal(UserGoal):

	def __init__(self, predicate_arguments, constraints, requestables):
		UserGoal.__init__(self, predicate_arguments, constraints, requestables)

	def update(self, last_system_action):
		self.satisfied = last_system_action.__class__ == CompleteTask


class UserAgenda:

	def __init__(self, goal, history, system_turns):
		self.goal = goal
		self.belief = dict.fromkeys(goal.constraints, None)
		self.inform = Inform({}, self.goal.get_entity(), name="inform",
					 predicate_arguments=self.goal.predicate_arguments)

		self.history	  = history
		self.system_turns = system_turns

	def get_unmet_constraints(self):
		belief, constr = self.belief, self.goal.constraints
		return [s for s in belief if belief[s] != constr[s]]

	def get_met_constraints(self):
		belief, constr = self.belief, self.goal.constraints
		return [s for s in belief if belief[s] == constr[s]]

	def is_goal_satisfied(self):
		return self.goal.satisfied

	def on_no_result(self, profile, belief):
		last_inform = self.history[-1]
		last_informed_slots = list(last_inform.data.keys())
		self.belief.update({s : None for s in last_informed_slots})

		belief.update({s : None for s in last_informed_slots})

		no_results = 0
		for turn in self.system_turns[-3:]:
			no_results += sum([1 if isinstance(action, Lookup) and not 									\
								action.data else 0 for action in turn])
		
		# if it's the third turn in a row where the system gives "no result",
		# we enforce all slots to have valid values wrt user's current config

		if no_results > 2:
			for slot in last_informed_slots:
				self.goal.resample(slot, 
				  conditioned_on=belief)
		else:
			random_slot = random.choice(last_informed_slots)
			_index  = last_informed_slots.index(random_slot)
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

		response = self.inform_slots(pool, profile, forced=pool)
		response.is_multichoice()
		return response

	def on_propose(self, opts, profile):
		constr = {k : v for k, v in self.goal.constraints 											\
							  .items() if v != DONT_CARE}
		suitables = []
		for opt in opts:
			if constr == {s : opt[s] for s in constr.keys()}:
				suitables.append(opt)
		
		if suitables:
			if profile.roll_for_deny_proposal():  # decline proposal
				met = self.get_met_constraints()
				if not met:
					msg = "no met constraints on propose"
					self._on_error_occurred(msg)

				rnd_constr = random.choice(met)
				self.goal.resample(rnd_constr)
				self.belief[rnd_constr] = None

			else:     # user will choose one of the proposed options
				response 	= None
				chosen 		= random.choice(suitables)
				choice 		= opts.index(chosen)  +  1
				can_request = bool(self.goal.requestables)

				if len(opts) == 1:    # one option = yes|no question
					answer_no = False
					if isinstance(self.history[-1], Inform):
						last_turn = self.history[-1]
						# can answer no only if user chose last turn
						answer_no = last_turn.entity == self.goal.get_entity()							\
									and 'index' in last_turn.data.keys() 								\
									and profile.roll_for_deny_proposal()

					response = Deny() if answer_no else Affirm()
					can_roll = not isinstance(self.history[-1], Question) 								\
							   and not answer_no and can_request
					# do not ask two questions in a row
					if can_roll and profile.roll_for_ask_question():
						response = Question(random.choice(self.goal.requestables),
												 self.goal.get_entity(), data={})
				
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

				elif can_request and profile.roll_for_ask_question():
					n = profile.roll_for_informativity()
					n = min(n,  len(chosen.keys()))
					data = [{'index' : choice}, {}]

					for i in range(n):
						k = random.choice(list(chosen.keys()))
						data[1][k] = chosen[k]
						del chosen[k]

					can_ask  = self.goal.requestables
					response = Question(random.choice(can_ask), 
										self.goal.get_entity(),
										data=random.choice(data))
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
					responses = [user_Request,
								 RequestBack]
					response = random.choice(responses)(slot,
						  			  self.goal.get_entity())
				else:
					req_slot_mentions = 0
					for turn in self.history[-2:]:
						if isinstance(turn, Inform):
							req_slot_mentions += sum([1 if s == slot else 0 for 						\
														s in turn.data.keys()])
					if req_slot_mentions > 1:
						self.goal.constraints[slot] = DONT_CARE
						# user informed slot twice,  but no result
						# so they say any value for the slot is ok
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
			to_update  = non_key_slots.pop(slot_index)
			self.goal.resample(to_update)
			self.belief[to_update] = None

		return self.on_more_updates(profile)

	def on_more_updates(self, profile):
		unmet_constraints = self.get_unmet_constraints()
		if not unmet_constraints:
			self.history.append(Deny())
			return self.history[-1]

		return self.inform_slots(unmet_constraints, profile)

	def uncoop_turn(self, profile, can_request=True):
		pool = list(self.belief.keys())
		n = profile.roll_for_informativity()

		to_inform  = []
		to_request = None
		for i in range(min(len(pool), n)):
			slot = pool.pop(random.randint(0, len(pool)-1))
			is_goal_sat  = self.goal.satisfied
			request_slot = can_request and to_request is None  											\
						   and isinstance(self.goal, StepGoal) 											\
						   and (not is_goal_sat or to_inform) 											\
						   and profile.roll_for_assistance()

			if request_slot:
				to_request = slot
			else:
				to_inform.append(slot)
				# resample constraint for informed slot
				if slot in self.get_met_constraints():
					self.goal.resample(slot)
					self.belief[slot] = None

		if to_inform and not to_request:
			response = self.inform_slots(to_inform, profile, 
									   	   forced=to_inform)
		elif to_inform and to_request:
			data = {k : self.goal.constraints[k] for k in to_inform}
			response = user_Request(to_request, self.goal.get_entity(),
			 												data=data)
			self.history.append(response)
			self.belief.update(data)

		elif not to_inform and to_request:
			response = user_Request(to_request, self.goal.get_entity())
			self.history.append(response)
		
		else:
			self._on_error_occurred("empty uncooperative user's turn")

		response.is_uncooperative()
		if not can_request:
			response.is_opener()

		return response

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
		self.system_turns = []
		self.history = []
		self.profile = profile
		self.agendas = [UserAgenda(goal, self.history, 
				 		self.system_turns) for goal in goals]

	def get_user_belief(self):
		return {k : v for agenda in self.agendas for k, 
					v  in agenda.belief.items()}

	def update_goals_state(self, turn):
		actions_with_entity = [a for a in turn if (hasattr(a, 'frame') 									\
							   and a.frame is not None) or hasattr(a,
							   'entity')]

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
		# system turn is lost from interference
		if self.profile.roll_for_input_corrupt():
			return Repeat() # do not save to history

		# react to last turn since this is a repetition
		if isinstance(turn[0], RepeatLastTurn):
			turn = turn[0].last_turn

		self.update_goals_state(turn)
		self.system_turns.append(turn)
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
				if p.roll_for_giveup():
					return GiveUp()

				entity = failed_lookup.frame.entity
				agenda = self.get_agenda(entity)
				agenda.on_no_result(p, self.get_user_belief())

			agenda = random.choice(self.agendas)
			return agenda.uncoop_turn(p, can_request=bool(self.history))

		# cooperative user reacts to system
		for action in turn:
			agenda = self.get_agenda(action.entity if hasattr(action, 'entity')							\
									 				  else action.frame.entity)
			if isinstance(action, Lookup) and not action.data:
				if p.roll_for_giveup():
					return GiveUp()
				agenda.on_no_result(p, self.get_user_belief())
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
		next_intent = Greet()
		self.im.send_intent(next_intent)
		while not self.state.is_user_satisfied():
			turn = self.im.read_actions()
			next_intent = self.state.update(turn)
			self.im.send_intent(next_intent)
			if isinstance(next_intent, GiveUp):
				break

		self.im.read_actions()
		if self.state.is_user_satisfied():
			self.im.send_intent(Bye())