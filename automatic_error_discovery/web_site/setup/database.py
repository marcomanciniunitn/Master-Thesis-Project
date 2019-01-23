import records, nltk
from threading import Lock
from nltk.corpus import wordnet as wn

DONT_CARE = "I don't care" # special slot value for constraint relaxation

def clean(v):
	v = str(v).replace("'", r"\'")
	return v

def is_value(v):
	return v is not None and v != DONT_CARE

def get_closest_to_source(source, targets, get_distance=False):
	if source in targets:
		return source

	closest  = source
	min_distance = max([len(target) for target in targets]) + 1
	for target in targets:
		distance = nltk.edit_distance(source, target)
		if  distance < min_distance:
			min_distance = distance
			closest = target

	return closest, min_distance if get_distance else closest

class Database:

	class __Database:

		def __init__(self, database):
			self.database = records.Database(database)

	__instance = None
	__knowledge_base = {}
	__instance_L = Lock()
	__metaschema = []
	__all_values = {}
	__kb_seed = []

	def __query(self, query):
		Database.__instance_L.acquire()
		try:
			results = Database.__instance.database.query(query)
			try: 
				results = results.as_dict()
			except: 
				Database.__instance_L.release()
				return True
		except:
			Database.__instance_L.release()
			return []

		Database.__instance_L.release()
		return results

	def __init__(self, database="mysql://user:pass@localhost:3306/database"):
		if not Database.__instance: 
			Database.__instance = Database.__Database(database)

			# download wordnet
			nltk.download("wordnet")
			# retrieve metadata for database schema
			Database.__metaschema = []
			dbname = database.split("/")[-1]
			tables = [t['TABLE_NAME'] for t in self.__query(("SELECT * " + 								\
					  			 "FROM information_schema.tables WHERE " + 								\
					  			   "table_schema = '{}'").format(dbname))]

			for table in tables:
				pkey = self.__query(("SELECT * FROM " + 
						"information_schema.table_constraints t LEFT " +								\
						"JOIN information_schema.key_column_usage k O" + 								\
						"N t.constraint_name = k.constraint_name AND " + 								\
						"t.table_name = k.table_name WHERE k.table_sc" +								\
						"hema = '{}' AND k.table_name = '{}' AND t.co" + 								\
						"nstraint_type = 'PRIMARY KEY'").format(dbname, table))

				columns = self.__query(("SELECT * FROM " +
						"information_schema.columns WHERE table_schem" + 								\
						"a = '{}' AND table_name = '{}'").format(dbname, table))
				
				Database.__metaschema.append({'table_name' : table,
										'pkey' : pkey[0]['COLUMN_NAME'] 								\
									if pkey else None, 'columns' : []})
				
				for column in columns:
					metadata = {'column_name' : column['COLUMN_NAME'], 
						 'type' : {'data_type' : column['DATA_TYPE']}}

					# add allowed values for enum-type columns
					if metadata['type']['data_type'] == "enum":
						row = self.__query(("SELECT TRIM(TRAILING ')' " + 
								"FROM TRIM(LEADING '(' FROM TRIM(LEADI" + 								\
								"NG 'enum' FROM column_type))) column_" +					 			\
								"type FROM information_schema.columns " +								\
								"WHERE table_schema = '{}' AND table_n" +				 				\
								"ame = '{}' AND column_name = '{}'").format(dbname, table, 
																column['COLUMN_NAME']))[0]
						
						values = sum([value.split(",") if isinstance(value, str) 						\
									  	   else value.decode("utf-8").split(",") 						\
									  			 for value in row.values()], [])

						metadata['type']['values'] = [value[1:-1] for value in values] 
					
					# if column is nullable and has no default, we set its default to null
					default = self.__query(("SELECT COLUMN_DEFAULT, " + 								\
								"IS_NULLABLE FROM information_schema" + 								\
								".columns WHERE table_schema = '{}' " + 								\
								"AND table_name = '{}' AND column_na" +									\
								"me = '{}'").format(dbname, table, 
										column['COLUMN_NAME']))[0]

					metadata['has_default'] =  default['COLUMN_DEFAULT'] is not None or					\
										   	  (default['COLUMN_DEFAULT'] is None and 					\
										   	   default['IS_NULLABLE'] == "YES")

					# if column is foreign key, retrieve referenced table and column and add it to the metadata
					fkey = self.__query(("SELECT * FROM " +
							"information_schema.table_constraints " + 									\
							"t LEFT JOIN information_schema.key_co" +									\
							"lumn_usage k ON t.constraint_name = k" + 									\
							".constraint_name AND t.table_name = k" + 									\
							".table_name WHERE k.table_schema = "	+	 								\
							"'{}' AND k.table_name = '{}' AND k."   +									\
							"column_name = '{}' AND t.constraint"   +									\
							"_type = 'FOREIGN KEY'").format(dbname, table, 
										 		 metadata['column_name']))
					if fkey: 
						metadata['refs'] = {'table' : fkey[0]['REFERENCED_TABLE_NAME'], 
										  'column' : fkey[0]['REFERENCED_COLUMN_NAME']}
					
					# adding to current table metadata the information about the column	
					Database.__metaschema[-1]['columns'].append(metadata)


	@staticmethod
	def get_instance(database="mysql://user:pass@localhost:3306/database"):
		return Database(database=database)

	def get_table_wname(self, table_name):
		return [m for m in Database.__metaschema 														\
			if m['table_name'] == table_name][0]

	def get_metaschema(self):
		return Database.__metaschema

	def is_column_key(self, table, column_name, include_pkey=True):
		if column_name == table['pkey']:
			return include_pkey

		for col in table['columns']:
			if col['column_name'] != column_name:
				continue
			if 'refs' in col.keys():
				return True

		return False

	def column_to_slot(self, column_name, table_name):
		return "{}::{}".format(table_name, column_name)

	def slot_to_column(self, slot_name):
		return slot_name.split("::")[1]

	def slot_to_table(self, slot_name):
		return slot_name.split("::")[0]

	def insert(self, table_name, constr):
		q_constr = {self.slot_to_column(k) : self.normalize_slot_value(k, v)							\
					 		   	  for k, v in constr.items() if is_value(v)}
		
		query = "INSERT INTO `{}` ({}) VALUES ({})"
		query = query.format(table_name, 
					", ".join(["`{}`".format(k) for k in q_constr.keys()]),
									", ".join(["'{}'".format(v) for k, v in 							\
														q_constr.items()]))
		return self.__query(query)

	def select(self, table_name, constr):
		q_constr = {self.slot_to_column(k) : self.normalize_slot_value(k, v)							\
					 		   	  for k, v in constr.items() if is_value(v)}
		
		query = "SELECT * FROM `{}` WHERE {}"
		query = query.format(table_name, 
							 " AND ".join(["`{}` = '{}'".format(k, v) 									\
							 		   for k, v in q_constr.items()]) 									\
							 					if q_constr else "1")
		rows = []
		for row in self.__query(query):
			rows.append({self.column_to_slot(k, table_name) : v for k, 
													v in row.items()})
		return rows

	def update(self, table_name, constr):
		q_where = self.get_table_wname(table_name)['pkey']
		q_constr = {self.slot_to_column(k) : self.normalize_slot_value(k, v)							\
					 		   	  for k, v in constr.items() if is_value(v)}
		
		query = "UPDATE `{}` SET {} WHERE {}"
		query = query.format(table_name, 
							 ", ".join(["`{}` = '{}'".format(k, v) for k, v 							\
							 in q_constr.items()]), "`{}` = '{}'".format(q_where, 
							 								  q_constr[q_where]))
		return self.__query(query)

	def delete(self, table_name, constr):
		q_constr = {self.slot_to_column(k) : self.normalize_slot_value(k, v)							\
					 		   	  for k, v in constr.items() if is_value(v)}
		
		query = "DELETE FROM `{}` WHERE {}"
		query = query.format(table_name, 
							 " AND ".join(["`{}` = '{}'".format(k, v) for k, v 							\
							 							in q_constr.items()]))
		return self.__query(query)

	def project(self, table_name, constr, target):
		target = ", ".join(["`{}`".format(self.slot_to_column(t)) 										\
					 	 for t in ([target] if isinstance(target, 										\
					 						  str) else target)])

		q_constr = {self.slot_to_column(k) : self.normalize_slot_value(k, v)							\
					 		   	  for k, v in constr.items() if is_value(v)}
		
		query = "SELECT DISTINCT {} FROM `{}` WHERE {}"
		query = query.format(target, table_name, 
							 " AND ".join(["`{}` = '{}'".format(k, v) for k, v 							\
							 		in q_constr.items()]) if q_constr else "1")
		rows = []
		for row in self.__query(query):
			rows.append({self.column_to_slot(k, table_name) : v for k, 
													v in row.items()})
		return rows

	def select_nth(self, table_name, constr, index):
		q_constr = {self.slot_to_column(k) : self.normalize_slot_value(k, v)							\
					 		   	  for k, v in constr.items() if is_value(v)}
		
		query = "SELECT * FROM `{}` WHERE {} LIMIT {}, 1"
		query = query.format(table_name, 
							 " AND ".join(["`{}` = '{}'".format(k, v) for k, v 							\
							 		in q_constr.items()]) if q_constr else "1", 
							 									int(index) - 1)
		return {self.column_to_slot(k, table_name) : v for k, v 										\
							  in self.__query(query)[0].items()}

	def query_to_dict(self, query_type, table_name, constr):
		return {'query_type' : query_type.lower(),
				'table_name' : table_name,
				'constr' : constr}

	def queries_from_dict(self, _dict):
		from_query_type = {'update' : self.update,
						   'insert' : self.insert,
						   'delete' : self.delete}

		for query in _dict['queries']:
			from_query_type[query['query_type']](query['table_name'],
												 	query['constr'])

	def build_knowledge_base(self, seed):

		def build_inner_join(table_name):
			table = self.get_table_wname(table_name)
			fkeys = [c for c in table['columns'] 
						  if 'refs' in c.keys()]
			
			inner_join = ""
			for fkey in fkeys:
				foreign_column = fkey['refs']['column']
				foreign_table = fkey['refs']['table']
				inner_join += (" INNER JOIN `{}` ON `{}`.`{}` = "
							   "`{}`.`{}`").format(foreign_table,
							 					   table['table_name'],
							 					   fkey['column_name'],
							 					   foreign_table,
							 					   foreign_column)

			for foreign_table in set([f['refs']['table'] for f in fkeys]):
				inner_join += build_inner_join(foreign_table)

			return inner_join

		Database.__kb_seed = seed
		for table_set in seed:
			root = table_set[0]
			query = "SELECT DISTINCT {} FROM " + root + 												\
								build_inner_join(root)
			
			for table in table_set:
				self.get_kb()[table] = query

	def kb_lookup(self, table_name, constr):
		table_set = [s for seed_set in self.get_kb_seed() for s in seed_set								\
												 if table_name in seed_set]

		q_constr = {"`{}`.`{}`".format(self.slot_to_table(k), self										\
					.slot_to_column(k)) : self.normalize_slot_value(k,
					  v) for k, v in constr.items() if is_value(v) and 									\
								    self.slot_to_table(k) in table_set}

		columns = ["`{}`.`{}`".format(table_name, c['column_name'])										\
				   for c in self.get_table_wname(table_name)['columns']]

		query = self.get_kb()[table_name].format(", ".join(columns)) 		+							\
				" WHERE {}".format(" AND ".join(["{} = '{}'".format(k, v) 								\
					   					for k, v in q_constr.items()]) if 								\
														q_constr else "1")
		rows = []
		for row in self.__query(query):
			rows.append({self.column_to_slot(k, table_name) : v for k, 
													v in row.items()})
		return rows

	def get_kb(self):
		return Database.__knowledge_base

	def get_kb_seed(self):
		return Database.__kb_seed

	def get_values_for(self, slot):
		column_name = self.slot_to_column(slot)
		table_name = self.slot_to_table(slot)
		table = self.get_table_wname(table_name)

		if self.is_column_key(table, column_name, include_pkey=False):
			for column in table['columns']:
				if column['column_name'] == column_name:
					ref_column = column['refs']['column']
					table_name = column['refs']['table']
					slot = self.column_to_slot(ref_column,
											   table_name)
					break

		if slot not in Database.__all_values:
			Database.__all_values[slot] = set([row[slot] for row in self								\
										 .project(table_name, {}, slot)])
		return Database.__all_values[slot]

	def normalize_slot_value(self, slot_name, source):
		""" 
			Gets all possible values for "column_name" and their
			synonyms. Then, it searches the closest column value
			to "source", or the column value that has a synonym
			that is the closest to "source"

		"""
		column_values = self.get_values_for(slot_name)
		
		if source in column_values:
			return clean(source)

		min_distance, closest = None, None
		for column_value in column_values:
			source = str(source)
			targets = [str(column_value)]
			for synset in wn.synsets(targets[-1]):
				for synonym in synset.lemma_names():
					targets.append(synonym.replace("_", r" "))
			
			_closest, _min_distance = get_closest_to_source(source,
									   targets, get_distances=True)

			if min_distance is None or _min_distance < min_distance:
				min_distance = _min_distance
				closest = column_value

		return clean(closest)