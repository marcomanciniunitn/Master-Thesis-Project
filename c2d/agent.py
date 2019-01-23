import operator, time, random

from database import Database, DONT_CARE
from intents import Inform, Request as user_Request, ThatsIt, Deny, 									\
					AskMoreOptions, AskPrevOptions,	AskHeadOptions,										\
					Affirm, DontCare, GiveUp, Question, Repeat, 										\
					RequestBack
from actions import Request as agent_Request, Bye as agent_Bye, Greet,  								\
					PollUpdates, MoreUpdates
from customs import Multichoice, ResetDependencies, RestorePreferences,									\
					TransferPreferences, BeginTask, Finalize, Lookup,									\
					CompleteTask, Delete, SaveChoice, Insert, Update,									\
					PrepareForUpdates, Propose, LoadMoreOptions,										\
					LoadPrevOptions, LoadHeadOptions, ReloadOptions,									\
					RelaxLastRequest, RepeatLastTurn, AnswerQuestion, 									\
					CustomAction

class DM():

	def __init__(self, im):
		self.im = im

	def prepare(self, frames):
		self.frames = frames
		for frame in frames:
			frame.clear()
		
		self.history = {'text' : [], 'turns': []}

	def run(self):

		actions = []
		self.im.read_intent()
		self._send([Greet()])

		while True:
			intent = self.im.read_intent()
			frame = None

			if isinstance(intent, Repeat):
				# do not use self._send for repeat! we don't want repetitions in the history
				repeat = RepeatLastTurn().run(self.history['turns'][-1],
											  self.history['text'][-1])
				self.im.send_actions([repeat])
				continue

			# first turn of conversation
			if not sum([f.history for f in self.frames], []):
				root_frame = self.get_root_frame()
				actions.append(BeginTask(root_frame).run(self.frames))
			
			if isinstance(intent, GiveUp):
				self._send([agent_Bye()])
				return

			elif isinstance(intent, ThatsIt):
				self._send([agent_Bye(), Finalize(None).run()])
				self.im.read_intent() # wait for bye back
				return

			elif isinstance(intent, Inform):
				actions.extend(self._update_belief(intent))

			elif isinstance(intent, DontCare):
				frame = self.get_current_frame()
				actions.append(RelaxLastRequest(frame).run())

			elif isinstance(intent, user_Request):
				to_append = self._update_belief(intent)
				inform_success = bool(to_append) and 													\
								 isinstance(to_append[-1], 
						 		 Lookup) and to_append[-1].data
				
				if not intent.data or inform_success:
					# multichoice only if no inform or inform succeeded
					frame  = self.get_frame(intent.entity)
					belief = self.get_system_belief()
					self._send(to_append + [Multichoice(frame, intent.slot,
										self.get_all_slots()).run(belief)])
					continue
				
				actions.extend(to_append)

			elif isinstance(intent, RequestBack):
				frame  = self.get_frame(intent.entity)
				belief = self.get_system_belief()
				self._send([Multichoice(frame, intent.slot,
						self.get_all_slots()).run(belief)])
				continue

			current_frame = self.get_current_frame()
			while current_frame and current_frame.is_frame_filled():                # complete all filled frames
				current_frame = None if not self.complete_subdialog(actions,
								current_frame) else self.get_current_frame()
			if current_frame is not None:                                           # fill current frame
				actions.append(agent_Request(current_frame.get_next_slot(), 
												 	 current_frame.entity))
			if self.get_current_frame() is None:
				actions.append(CompleteTask(self.get_root_frame()).run())

			if self.im.peek_intent() is None:
				self._send(actions)
				actions = []

	def complete_subdialog(self, actions, frame):
		if frame.subdialog.lower() == "insert":
			actions.append(Insert(frame).run())
			frame.complete_frame()
			return True

		elif frame.subdialog.lower() == "delete":
			if self._elicit_user_preference(frame, actions):
				actions.append(Delete(frame).run())
				frame.complete_frame()
				return True

			return False

		elif frame.subdialog.lower() == "select":
			if self._elicit_user_preference(frame, actions):
				actions.append(SaveChoice(frame).run())
				frame.complete_frame()
				
				if frame.parent:
					actions.append(TransferPreferences(frame).run())
				
				return True

			return False

		elif frame.subdialog.lower() == "update":
			if self._elicit_user_preference(frame, actions):
				self._send([PrepareForUpdates(frame).run(),
							PollUpdates(frame.entity)])
				intent = None
				while not isinstance(intent, Deny):
					intent = manager.read_intent()
					if isinstance(intent, Inform):
						frame.update(intent.data)
						self._send([MoreUpdates(frame.entity)])

				actions.append(Update(frame).run())
				frame.complete_frame()
				return True

			return False

	def get_frame(self, entity):
		for frame in self.frames:
			if frame.entity == entity:
				return frame

		raise ValueError("No frame with entity '{}' was found".format(entity))

	def get_root_frame(self):
		return [frame for frame in self.frames if not frame.parent][0]

	def get_final_frame(self):
		return self.get_frame(sorted({frame.entity : frame.fill_order 
								   for frame in self.frames}.items(), 
								          key=operator.itemgetter(1),
										  		 reverse=True)[0][0])

	def get_current_frame(self):
		filling_order = sorted({frame.entity : frame.fill_order 						                \
									for frame in self.frames if 										\
										 frame.active}.items(),
							  	   	key=operator.itemgetter(1))
		
		return self.get_frame(filling_order[0][0])														\
			 			if filling_order else None

	def get_all_slots(self, exclude_fkeys=False):
		return sum([frame.get_all_slots(exclude_fkeys=exclude_fkeys) 									\
				    for frame in self.frames], [])

	def get_system_belief(self):
		return {k : frame.content[k] for frame in self.frames 											\
									  for k in frame.content}

	def get_pretty_system_belief(self):
		return {k: v for k, v in Database.get_instance() 											 	\
			   .join_result_set_on_fkeys(self 															\
			   .get_system_belief()).items() 															\
			   if k in self.get_all_slots()}

	def _elicit_user_preference(self, frame, actions):
		belief = self.get_system_belief()
		actions.append(Propose(frame).run(belief))
		self._send(actions)
		del actions[:]

		while 1:
			# wait for user intent
			while not self.im.peek_intent():
				time.sleep(0.01)
	        
			intent = self.im.peek_intent()
			if isinstance(intent, Inform):
				if 'index' in intent.data.keys():
					self.im.read_intent()
					frame.save_choice(intent.data['index'] - 1)
					self._send([Propose(frame).run(self.get_system_belief())])
				else:
					# slots of different frame and changed preferences
					updates = [k for k in intent.data.keys() if intent.entity                      		\
							   != frame.entity or (k in frame.get_all_slots() 							\
							   		  and intent.data[k] != frame.content[k]) 							\
							    	  and frame.content[k] is not None]
					if updates:
						return False

					self.im.read_intent()
					a = self._update_belief(intent)
					a.append(Propose(frame).run(self 													\
							  .get_system_belief()))
					self._send(a)

			elif isinstance(intent, Question):
				self.im.read_intent()
				answer  = AnswerQuestion(frame, intent.slot).run(intent.data)
				propose = Propose(frame).run(self.get_system_belief())
				self._send([answer, propose])

			elif isinstance(intent, Affirm): 
				self.im.read_intent()
				return True

			elif isinstance(intent, Deny):
				self.im.read_intent()
				a = ReloadOptions(frame).run()
				belief = self.get_system_belief()
				self._send([a, Propose(frame).run(belief)])

			elif isinstance(intent, AskMoreOptions):
				self.im.read_intent()
				belief = self.get_system_belief()
				self._send([LoadMoreOptions(frame).run(),
							Propose(frame).run(belief)])

			elif isinstance(intent, AskPrevOptions):
				self.im.read_intent()
				belief = self.get_system_belief()
				self._send([LoadPrevOptions(frame).run(),
							Propose(frame).run(belief)])

			elif isinstance(intent, AskHeadOptions):
				self.im.read_intent()
				belief = self.get_system_belief()
				self._send([LoadHeadOptions(frame).run(),
							Propose(frame).run(belief)])
			elif isinstance(intent, Repeat):
				self.im.read_intent()
				self.im.send_actions([RepeatLastTurn() 													\
					   .run(self.history['turns'][-1],
							self.history['text'][-1])])
			else:        
				return False

	def _update_belief(self, intent):
		if not intent.data:
			return [] # add code for corrupted user message here

		actions = []
		frame = self.get_frame(intent.entity)
		if not frame.active and frame.parent:
			actions.extend(RestorePreferences(frame).run(intent.data))
			actions.append(Lookup(frame).run(self.get_system_belief()))
		else:
			frame.update(intent.data)
			if isinstance(frame, ExtendedFrame):
				actions.extend([ResetDependencies(frame).run(),
								Lookup(frame).run(self
							   .get_system_belief())])
		return actions

	def _send(self, actions):
		if actions:
			text = " ".join([(a.to_natural_language() if isinstance(a, 
					CustomAction) else random.choice(a.templates)) for 									\
														a in actions])
			self.history['text'].append(text)
			self.history['turns'].append([a for a in actions])

		self.im.send_actions(actions)

	def _on_error_occurred(self, msg):
		msg = msg + "\nsystem belief: {}".format(self.get_system_belief())
		raise ValueError(msg)


class Frame:

	def __init__(self, entity, slots, fill_order, priorities, 
									subdialog, parent=None):
		self.slots  = slots
		self.entity = entity
		self.parent = parent
		self.subdialog  = subdialog
		self.fill_order = fill_order
		self.priorities = priorities
		
		db = Database.get_instance()
		self.table = db.get_table_wname(entity)
		self.content = {db.column_to_slot(column['column_name'],
							self.table['table_name']) : None for                                        \
								column in self.table['columns']}

	def __eq__(self, other):
		return isinstance(other, Frame) and 															\
				self.entity == other.entity

	def __hash__(self):
		return hash(self.entity)

	def clear(self):
		self.content = dict.fromkeys(self.content, None)
		self.active = True
		self.history = []

	def update(self, info):
		self.snapshot()
		self.content.update({k : v for k, v in info.items() 										    \
							  if k in self.content.keys()})

	def rewind(self):
		self.content = self.history.pop()

	def snapshot(self):
		self.history.append({k : v for k, v in self.content.items()})

	def get_next_slot(self):
		slots = self.get_all_slots()
		max_filled = 0
		for _slots in self.slots:
			filled = sum([0 if self.content[s] is None 
							  else 1 for s in _slots])
			if filled > max_filled:
				max_filled = filled
				slots = _slots

		return sorted({k : v for k, v in self.priorities.items()						                \
					   if self.content[k] is None and k in slots}										\
					  .items(), key=operator.itemgetter(1))[0][0]

	def get_all_slots(self, exclude_fkeys=False):
		slots = sum(self.slots, [])
		if exclude_fkeys:
			db = Database.get_instance()
			tname = self.table['table_name']
			fkeys = [db.column_to_slot(col['column_name'], tname) for col 								\
					 in self.table['columns']  if col.get('refs', False)]
			slots = [slot for slot in slots if slot not in fkeys]

		return slots

	def get_informable_slots(self):
		db = Database.get_instance()
		return [slot for slots in self.slots for slot in slots if not
				db.is_column_key(self.table, db.slot_to_column(slot),
												include_pkey=False)]

	def complete_frame(self):
		self.active = False
		if self.parent is not None:
			self.parent.active = True

	def restore_frame(self):
		self.active = True

	def is_frame_filled(self):
		for slots in self.slots:
			nones = [1 if self.content[s] is None else 													\
					 	   			 0 for s in slots]
			if not sum(nones):
				return True
		
		return False

	def get_infod_content(self):
		return {k : v for k, v in self.content.items() if v is not None}

	def get_infod_slots(self):
		return {k : self.content[k] for k in self.slots if 												\
							  self.content[k] is not None}

	def get_empty_slots(self):
		return [k for k, v in self.content.items() if k in 												\
						self.get_all_slots() and v is None]

	
class ExtendedFrame(Frame):

	def __init__(self, entity, slots, fill_order, priorities, dependencies,
				  requestables, subdialog, parent=None, results_to_show=3):
		
		Frame.__init__(self, entity, slots, fill_order, priorities, 
										  subdialog, parent=parent)
		self.dependencies = dependencies
		self.requestables = requestables
		self.result_set = []
		self.results_offsets = [0]
		self.results_to_show = results_to_show

	def clear(self):
		self.clear_navigation_history()
		Frame.clear(self)

	def get_requestable_slots(self):
		return self.requestables

	def clear_navigation_history(self):
		self.results_offsets = [0]

	def save_choice(self, index):
		self.update(self.get_results_to_show()[index])
		self.clear_navigation_history()

	def get_results_to_show(self):
		end   = self.results_offsets[-1] + self.results_to_show
		start = self.results_offsets[-1]
		return self.result_set[start:end]

	def can_advance_results_list(self):
		cur_offset = self.results_offsets[-1]
		return self.result_set[cur_offset:] != self.get_results_to_show()

	def can_restore_results_list(self):
		return len(self.results_offsets) > 1

	def advance_results_list(self):
		if self.can_advance_results_list():
			new_offset = self.results_offsets[-1] + self.results_to_show
			self.results_offsets.append(new_offset)

	def restore_results_list(self):
		if self.can_restore_results_list():
			del self.results_offsets[-1]

	def to_results_list_head(self):
		self.results_offsets.append(0)