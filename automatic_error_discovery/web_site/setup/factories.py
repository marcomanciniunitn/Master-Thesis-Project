from agent import Frame, ExtendedFrame
from intents import Inform
from database import Database
from simulator import UserGoal, StepGoal, EndGoal

import random

class FrameFactory:

	def build_frames(self, task):
		frames = []
		self.__build_frames(task['task_tree'], frames)
		return frames

	def __build_frames(self, subtask, frames):
		slots = subtask['slots']
		table_name = subtask['table']
		
		db = Database.get_instance()
		slots = [[db.column_to_slot(slot, table_name) for slot in _slots]								\
													 for _slots in slots]
		priorities = {db.column_to_slot(s, table_name) : v for                                     		\
                        s, v in subtask['priorities'].items()}

		# auto dependencies
		dependencies = {}
		for slot in set(sum(subtask['slots'], [])):
			appears_with = set(sum([slots for slots in subtask['slots']
											 	if slot in slots], []))
			dependencies[slot] = set([slot for slots in subtask['slots'] for 
						  		  	  slot in slots if slot not in 
						  		  	  appears_with])
		# manual dependencies
		# dependencies = subtask['dependencies']
		dependencies = {db.column_to_slot(s, table_name) :                                         		\
						[db.column_to_slot(v, table_name)                                         		\
						 for v in dependencies[s] if v in 												\
						 sum(subtask['slots'], [])] for s                                         		\
						   in dependencies.keys() if s in 												\
							   sum(subtask['slots'], [])}
		"""
		pkey = db.column_to_slot(db.get_table_wname(table_name)['pkey'],
		 													 table_name)
		for slot in dependencies:
			if pkey not in dependencies[slot]:
				dependencies[slot].append(pkey)
		"""
		entity = table_name
		parent = frames[-1] if frames else None

		if subtask['operation'] == "insert":
			frame = Frame(entity, slots, subtask['frame_priority'], priorities, 
										   subtask['operation'], parent=parent)
		else:
			frame = ExtendedFrame(entity, slots, subtask['frame_priority'], 
							priorities, dependencies, subtask['operation'], 
								  						  	parent=parent)
		frames.append(frame)
		for child in subtask['children']:
			_frames = [frame]
			self.__build_frames(child, frames=_frames)
			frames += _frames[1:]


class GoalFactory:

	def __init__(self):
		self.goal_map = {'select' : StepGoal,
						 'insert' : EndGoal,
						 'delete' : EndGoal,
						 'update' : EndGoal}

	def build_goals(self, task):
		goals = []
		task_predicate_arguments = task['predicate_argument']
		task_predicate_arguments.insert(0, {'predicate' : task['operation'],
										 	'argument'  : task['table']})
		
		self.__build_goals(task['task_tree'], goals, 
						   task_predicate_arguments)

		return goals


	def __build_goals(self, subtask, goals, task_predicate_argument):
		db = Database.get_instance()
		
		predicate_argument  = {'predicate' : subtask['operation'],
							   'argument'  : subtask['table']}

		predicate_arguments = {'subdialog' : [], 'dialog' : []}
		predicate_arguments['dialog'].extend(task_predicate_argument)
		predicate_arguments['subdialog'].append(predicate_argument)
		predicate_arguments['subdialog'].extend(subtask													\
						.get('predicate_argument', []))

		constraints = dict.fromkeys(random.choice(subtask['slots']), None)
		table = db.get_table_wname(subtask['table'])
		constraints = {db.column_to_slot(k, subtask['table']) : v for k,
										v in constraints.items() if not 
											 db.is_column_key(table, k,
												   include_pkey=False)}

		goals.append(self.goal_map[subtask['operation']](predicate_arguments,
								 						  		constraints))
		for child in subtask['children']:
			self.__build_goals(child, goals, task_predicate_argument)

