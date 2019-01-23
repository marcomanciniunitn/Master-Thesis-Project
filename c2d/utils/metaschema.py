from threading import Thread

from database import Database

import argparse
import json

def main():

	parser = argparse.ArgumentParser()

	parser.add_argument("db_name", help="Name of the db")
	parser.add_argument("meta_file", help="Filename for the meataschema DB file dump")

	args = parser.parse_args()

	db = Database.get_instance(database="mysql://root:root@localhost:3306/{}".format(args.db_name))

	with open(args.meta_file, "w+") as f:
		json.dump(db.get_metaschema(), f)

if __name__ == "__main__":
	main()