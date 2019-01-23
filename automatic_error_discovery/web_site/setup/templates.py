propose_run_template = """
        slots = {slots}

        from database import Database, is_value
        db = Database.get_instance() 
        matches = tracker.get_slot("matches")

        if matches is None:
            matches = matches if matches else db.kb_lookup({table_name},
                            {{s : tracker.get_slot(s) for s in slots}})
        rows = matches

        if rows:
            from rasa_core.events import SlotSet
            events = [SlotSet("user_choice", None)]
            events.append(SlotSet("matches", matches))

            user_choice = tracker.get_slot("user_choice")
            to_show = tracker.get_slot("results_displayed")
            offsets = tracker.get_slot("results_offsets")
            offset = offsets[-1]

            rows = rows[offset:offset + to_show]
            if user_choice:
                rows = [rows[int(user_choice) - 1]]
                events.append(SlotSet("results_offsets", [0]))
             
            if len(rows) == 1:
                message = "Is this {table_name} what you were" +                                        \\
                                               " looking for?"
            else:
                message = "There are more than one {table_name} with "   +                              \\
                          "{{}}. Here, let me show you:".format((" and " +                              \\
                          "").join(["{{}} {{}}".format(s, tracker.get_slot(s))
                                              for s in slots if is_value(s)]))            
            dispatcher.utter_message(message)
            for i, row in enumerate(rows):
                prompt = "({{}}) ".format(i + 1)
                for name, value in row.items():
                    prompt += "{{}}: {{}}; ".format(name, value)

                dispatcher.utter_message(prompt + "\\n")

            if len(rows) > 1:
                dispatcher.utter_message("Feel free to choose any "
                                         "option from the list.")
            if matches[offset + to_show:]:
                dispatcher.utter_message("I also have more options similar to the ones "
                                         "you are seeing. Just ask me to show you more "
                                         "if you can't find what you're looking for here.")
            if len(offsets) > 1:
                dispatcher.utter_message("If you want to go back to see the previous option"
                                         "s or the first options of the list, just ask me.")
            return events

        dispatcher.utter_message("Sorry, but I couldn't find anything")
        return []

        """

delete_run_template = """
        from rasa_core.events import UserUtteranceReverted, SlotSet
        matches = tracker.get_slot("matches")
        if matches is None:
            dispatcher.utter_message("I'm sorry, I didn't catch that")
            return [UserUtteranceReverted()]

        from rasa_core.events import SlotSet
        from database import Database
        db = Database.get_instance() 
        choice = matches[0]

        dispatcher.utter_message("Ok. As you requested I have registered your "
                                 "cancellation for the following {table_name}:"
                                 " {{}}".format(" and ".join(["{{}} {{}}"
                                 "".format({{k : v for k, v in choice.items()}})])))

        queries = tracker.get_slot("queries")
        queries.append(db.query_to_dict("delete", "{table_name}", choice))

        return [SlotSet("matches", None),
                SlotSet("queries", queries)]
        
        """

update_run_template = """
        from database import Database, is_value
        pk = tracker.get_slot("{pkey}")
        db = Database.get_instance() 
        slots = {slots}
        
        if pk is None:
            dispatcher.utter_message("I couldn't find the {table_name} "
                                     "you were looking to change")
            return []
        
        dispatcher.utter_message("Alright. I took note of your changes as requested."
                                 " Your {table_name} now looks like this: {{}}"
                                 "".format(" and ".join(["{{}} {{}}"
                                 "".format({{s : tracker.get_slot(s) for s in slots                     \\
                                            if is_value(tracker.get_slot(s))}})])))
        
        queries = tracker.get_slot("queries")
        queries.append(db.query_to_dict("update", "{table_name}",
                      {{s : tracker.get_slot(s) for s in slots}}))

        from rasa_core.events import SlotSet
        return [SlotSet("queries", queries)]

        """

insert_run_template = """
        from database import Database, is_value
        db = Database.get_instance() 
        slots = {slots}

        dispatcher.utter_message("Ok. As requested by you, I have registered your "
                                 "{table_name} for {{}}".format(" and ".join(["{{}}"
                                 " {{}}".format(s, tracker.get_slot(s)) for s in slots                  \\
                                                 if is_value(tracker.get_slot(s))])))
        queries = tracker.get_slot("queries")
        queries.append(db.query_to_dict("insert", "{table_name}", 
                      {{s : tracker.get_slot(s) for s in slots}}))
        
        from rasa_core.events import SlotSet
        return [SlotSet("queries", queries)]

        """

multichoice_run_template = """
        from database import Database, is_value
        db = Database.get_instance() 

        slots  = {slots}
        target = {target}
        user_config = {{s : tracker.get_slot(s) for s in slots}}
        results = db.project("{table_name}", user_config, target)
        if not results:
            results = db.project("{table_name}", {{}}, target)
            if not results:
                from rasa_core.events import UserUtteranceReverted
                return [UserUtteranceReverted()]

        options = ""
        for row in results:
            options += ", ".join(list(row.values()))

        dispatcher.utter_message("You can choose among the following"
                                 " {{}}s: {{}}".format(target, 
                                 options.strip(", ")))
        
        from rasa_core.events import SlotSet
        return []

        """

savechoice_run_template = """
        from rasa_core.events import UserUtteranceReverted, SlotSet
        matches = tracker.get_slot("matches")
        if matches is None:
            dispatcher.utter_message("Sorry, I didn't catch that")
            return [UserUtteranceReverted()]

        dispatcher.utter_message("Ok! You have selected the "
                                 "following {table_name}:")
        
        choice = matches[0]
        events = []
        for slot, value in choice.items(): 
            dispatcher.utter_message("{{}}: {{}}".format(slot, value))
            events.append(SlotSet(slot, value))
        
        return events + [SlotSet("matches", None)]

        """

resetdependencies_run_template = """
        dependencies = {dependencies}
        from utils.state_history import StateHistory
        updated = StateHistory().get_updated_slots(tracker)

        from database import DONT_CARE
        ignore = [k for k in updated.keys() if updated[k] == DONT_CARE]
        to_check = [k for k in updated.keys() if k not in ignore]

        from rasa_core.events import SlotSet

        resets = []
        for k in to_check:
            for dep in dependencies.get(k, []):
                if dep not in updated.keys():
                    resets.append(SlotSet(dep, None))
        
        return resets
        
        """

lookup_run_template = """
        from database import Database, is_value
        slots = {slots}
        db = Database.get_instance() 
        matches = db.kb_lookup("{table_name}", {{s : tracker.get_slot(s)                                \\
                                                       for s in slots}})
        from utils.state_history import StateHistory
        from rasa_core.events import SlotSet
        if not matches:
            last_set_slots = StateHistory().get_events(tracker, 
                             event_type='user')[-1]['parse_data']['entities']
            configuration = " and ".join(["{{}} {{}}".format(s, 
                            tracker.get_slot(s)) for s in slots                                         \\
                            if is_value(tracker.get_slot(s))])
            
            dispatcher.utter_message("Unfortunately, I couldn't find any"
                                     " {table_name} with {{}}"
                                     "".format(configuration))

            return [SlotSet(e['entity'], None) for e in last_set_slots]
            
        import random
        prompts = ["Alright, got that", "Understood", "Mm-mmh"]
        dispatcher.utter_message(random.choice(prompts))

        return [SlotSet("matches", matches), SlotSet("results_offsets", [0])]

        """

prepareforupdates_run_template = """
        from rasa_core.events import UserUtteranceReverted, SlotSet
        matches = tracker.get_slot("matches")
        if matches is None:
            dispatcher.utter_message("I'm sorry, I didn't catch that")
            return [UserUtteranceReverted()]

        from database import Database
        db = Database.get_instance() 
        choice = matches[0]
        events = []

        table_name = "{table_name}"
        pkey = db.get_table_wname(table_name)['pkey']
        pkey = db.column_to_slot(pkey, table_name)

        dispatcher.utter_message("So you want to modify the following {table_name}:")
        for slot, value in choice.items(): 
            events.append(SlotSet(slot, None if slot != pkey else value))
            dispatcher.utter_message("{{}}: {{}}".format(slot, value))
        
        return events + [SlotSet("matches", None)]

        """

restorepreferences_run_template = """
        from database import Database
        db = Database.get_instance()
        events = []

        table_name = "{table_name}"
        table = db.get_table_wname(table_name)
        pkey = db.column_to_slot(table['pkey'], table_name)

        fkey = None
        for column in db.get_table_wname("{parent_name}")['columns']:
            if column.get('refs', {{}}).get('table', "") == table_name:
                if column['refs']['column'] == table['pkey']:
                    fkey = db.column_to_slot(column['column_name'],                                     \\
                                                   "{parent_name}")
        if not fkey:
            dispatcher.utter_message("Sorry, I didn't catch that")
            return []

        events.append(SlotSet(fkey, None))
        preferences = db.select_nth(table_name, 
          {{pkey : tracker.get_slot(fkey)}}, 1)

        dependencies = {dependencies}
        from utils.state_history import StateHistory
        updated = StateHistory().get_updated_slots(tracker)
        for slot in updated:
            deps = dependencies.get(slot, [])
            for dep in deps:
                events.append(SlotSet(dep, None))

        from rasa_core.events import SlotSet
        for slot, value in preferences.items():
            events.append(SlotSet(slot, value))

        return events

        """

transferpreferences_run_template = """
        from database import Database
        db = Database.get_instance() 
        events = []

        table_name = "{table_name}"
        table = db.get_table_wname(table_name)
        pkey = db.column_to_slot(table['pkey'], table_name)

        fkey = None
        for column in db.get_table_wname("{parent_name}")['columns']:
            if column.get('refs', {{}}).get('table', "") == table_name:
                if column['refs']['column'] == table['pkey']:
                    fkey = db.column_to_slot(column['column_name'],
                                                   "{parent_name}")
        if not fkey:
            dispatcher.utter_message("Sorry, I didn't catch that")
            return []

        preferences = db.select_nth(table_name, {{}}, 1)
        preferences = dict.fromkeys(preferences, None)

        slots = {slots}
        events.append(SlotSet(fkey, tracker.get_slot(pkey)))
        events.extend([SlotSet(s, None) for s in slots])
        return events 

        """

relaxlastrequest_run_template = """
        from utils.state_history import StateHistory
        last_request = StateHistory().get_latest_action()

        import re
        r = re.search("utter_ask_(.+::.+)", last_request)
        if r:
            last_requested_slot = r.group(1)
        else:
            from rasa_core.events import UserUtteranceReverted
            dispatcher.utter_message("Sorry, I didn't catch that")
            return [UserUtteranceReverted()]

        from rasa_core.events import SlotSet
        from Database import DONT_CARE
        return [SlotSet(last_requested_slot, DONT_CARE)]

        """

reloadoptions_run_template = """
        from rasa_core.events import SlotSet
        return [SlotSet(k, None) for k in {unfeaturized_slots}]

        """

begintask_run_template = """
        from database import Database
        from rasa_core.events import SlotSet
        db = Database.get_instance().build_knowledge_base({kb_seed})
        dispatcher.utter_message("Alright. So you want to {subdialog}"
                                                    " a {table_name}")
        return [SlotSet("queries", []),
                SlotSet("results_offsets", [0]),
                SlotSet("results_displayed", 3)]

        """

completetask_run_template = """
        dispatcher.utter_message("Now, is there anything else I can "
                                 "help you with or should I finalize?")
        # change this to manipulate dialog state reset at task completion
        from rasa_core.events import AllSlotsReset, SlotSet
        return [SlotSet("results_displayed", tracker.get_slot("results_displayed")),
                AllSlotsReset, SlotSet("queries", tracker.get_slot("queries")),
                SlotSet("results_offsets", [0])]

        """

finalize_run_template = """
        # uncomment this if you want queries that modify the database to be run
        #from database import Database
        #Database.get_instance().queries_from_dict(tracker.get_slot("queries"))
        from rasa_core.events import SlotSet
        return [SlotSet("queries", [])]

        """

loadmoreoptions_run_template = """
        from rasa_core.events import SlotSet, UserUtteranceReverted

        n_matches = len(tracker.get_slot("matches"))
        cur_offsets = tracker.get_slot("results_offsets")
        n_res_shown = tracker.get_slot("results_displayed")

        if cur_offsets[-1] + n_res_shown > n_matches:
            dispatcher.utter_message("There is no other new result. Let me "
                                     "know if you want to see previous resu"
                                     "lts or move back to the beginning of "
                                     "the result list")
            
            return [UserUtteranceReverted()]

        new_offset = cur_offsets[-1] + n_res_shown
        cur_offsets.append(new_offset)

        if n_matches - cur_offsets[-1] > n_res_shown:
            dispatcher.utter_message("Ok, I'll show you the next {} results"
                                     "".format(n_res_shown))
        else:
            dispatcher.utter_message("Ok, I'll show you the last results")

        return [SlotSet("results_offsets", cur_offsets)]

        """

loadprevoptions_run_template = """
        from rasa_core.events import SlotSet, UserUtteranceReverted
        cur_offsets = tracker.get_slot("results_offsets")

        if len(cur_offsets) == 1:
            dispatcher.utter_message("You are currently looking at the first results."
                                     " I can not go back")
            
            return [UserUtteranceReverted()]

        del cur_offsets[-1]
        dispatcher.utter_message("Ok, I'll show you the previous {} results"
                                 "".format(tracker.get_slot("results_displayed")))
        
        return [SlotSet("results_offsets", cur_offsets)]

        """

loadheadoptions_run_template = """
        from rasa_core.events import SlotSet
        cur_offsets = tracker.get_slot("results_offsets")

        if cur_offsets[-1] != 0:
            cur_offsets.append(0)
            dispatcher.utter_message("Ok, I'll show you the first {} results"
                                     "".format(tracker.get_slot("results_displayed")))

            return [SlotSet("results_offsets", cur_offsets)]

        dispatcher.utter_message("You are already looking at the first results")
        return []

        """