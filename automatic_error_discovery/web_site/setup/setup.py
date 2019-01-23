from factories import GoalFactory, FrameFactory
from simulator import UserGoal
from database import Database

import argparse
import json
import os

from_ID = 0


def generate_IDs(n, user_file="/var/www/feedback/setup/users.txt"):
	global from_ID

	with open(user_file, "w+") as f:
		for i in range(from_ID, int(n) + from_ID):
			f.write("user_{}\n".format(i))

	os.chmod(user_file, 0o777)

def get_all_slots(db):
		
		meta = db.get_metaschema()
		slots = []
		for table in meta:
			t_name = table['table_name']
			for col in table['columns']:
				if not db.is_column_key(table, col):
					slots.append(t_name + "::" + col['column_name'])

		return slots

def generate_goals_belief(n, db, features, general_goal, goal_folder="/var/www/feedback/goals", belief_folder="/var/www/feedback/beliefs"):
	
	goal_factory = GoalFactory()
	frame_factory = FrameFactory()

	with open(features, "r") as f:
		functionalities = json.load(f)['tasks']

	slots = set()

	goals, frames = [], []
	global from_ID

	for dial in range(from_ID, int(n) + from_ID):
		for func in functionalities:
			goals.append(goal_factory.build_goals(func))
			frames.append(frame_factory.build_frames(func))
			if len(slots) == 0:
				for a in frames:
					for fr in a:
						for sl in fr.slots:
							for s in sl:
								print(s)
								if s.split("::")[1].find("fk") == -1:
									slots.add(s)


			for goal, frame in zip(goals[-1], frames[-1]):
				for slot in goal.constraints.keys():
					
					goal.resample(slot)
					goal_to_dump = {"goal": general_goal}
					belief_to_dump = {}

					goal_slots = {}
					for frame_goal in goals[-1]:
						for constr, value in frame_goal.constraints.items():
							goal_slots[constr] = value
							belief_to_dump[constr] = "?"
						for sl in slots:
							print(sl)
							if sl not in belief_to_dump.keys():
								belief_to_dump[sl] = "?"
								goal_slots[sl] = "ANY VALUE YOU WANT"
			
							
					goal_slots = dict(sorted(goal_slots.items()))
					belief_to_dump = dict(sorted(belief_to_dump.items()))

					goal_to_dump['slots'] = goal_slots

					with open("{}/user_{}".format(goal_folder, dial), "w+") as f:
						json.dump(goal_to_dump,f)

					os.chmod("{}/user_{}".format(goal_folder, dial), 0o777)

					with open("{}/user_{}".format(belief_folder, dial), "w+") as f:
						json.dump(belief_to_dump, f)

					os.chmod("{}/user_{}".format(belief_folder, dial), 0o777)


def main():

	parser = argparse.ArgumentParser()
	
	parser.add_argument("n", type=int, help="Samples per functionality")
	parser.add_argument("from_n", type=int, help="Initial ID")
	parser.add_argument("db_name", help="Name of the database to use")
	parser.add_argument("features", help="Path to json file with bot features")

	parser.add_argument("-goal", default="/var/www/feedback/setup/goal.txt", help="Path for goal file" )

	parser.add_argument("-db_ip", default="localhost", help="Database address")
	parser.add_argument("-db_pwd", default="root", help="User's password")
	parser.add_argument("-db_user", default="root", help="Database user")
	parser.add_argument("-db_port", default="3306", help="Database port")



	args = parser.parse_args()
	database = "mysql://{}:{}@{}:{}/{}".format(args.db_user, args.db_pwd, 
								  args.db_ip, args.db_port, args.db_name)

	global from_ID
	from_ID = args.from_n

	db = Database.get_instance(database=database)

	generate_IDs(args.n)

	with open(args.goal, "r") as f:
		goal = f.read()


	generate_goals_belief(args.n, db, args.features, goal)

	
if __name__ == "__main__":
	main()