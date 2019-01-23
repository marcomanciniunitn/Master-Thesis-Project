from database import Database, DONT_CARE, is_value
from actions import Action
from intents import Affirm, Inform, Deny, AskMoreOptions,                                       \
                          AskPrevOptions, AskHeadOptions
import templates
import json, random


class CustomAction(Action):

    _VUIDM_TEMPLATE = ("class {class_name}(Action):\n\n"                        +                       \
                       "    def name(self):\n"                                  +                       \
                       "        return \"{action_name}\"\n\n"                   +                       \
                       "    def run(self, dispatcher, tracker, domain):"        +                       \
                       "        {run_corpus}\n")

    def __init__(self, name, frame):
        Action.__init__(self, name)
        self.slot_events = {}
        self.frame = frame
        self.data = []

    def to_natural_language(self):
        return self.to_string()

    def to_string_verbose(self):
        return self.to_string()

    def to_python_code(self):
        return self._VUIDM_TEMPLATE.format(run_corpus=self.vui_dm_run(),
                            action_name=self.name, class_name=self.name)

    def to_string(self):
        slot_events = [" - slot{}".format(json.dumps({k : v}))                                          \
                         for k, v in self.slot_events.items()]

        return self.name + ("\n" if slot_events else "") + "\n".join(slot_events)

    def run(self):
        pass

    def vui_dm_run(self):
        pass

class Propose(CustomAction):

    def __init__(self, frame):
        table_name = frame.table['table_name']
        table_name = "".join([x.capitalize() for x in table_name.split("_")])
        name = "Propose{}".format(table_name)

        CustomAction.__init__(self, name, frame)

    def to_natural_language(self):
        prompt = ""
        user_config = " and ".join(["{}: {}".format(k, v) for k, v in                                   \
                                    self.last_system_belief.items()                                     \
                                    if k in self.frame.content                                          \
                                    .keys() and is_value(v)])
        if len(self.data) == 1:
            prompt += ("is this {} what you were looking"
                       " for?").format(self.frame.entity)
        else:
            prompt += ("there are more than one {} with {}. here:"
                       "").format(self.frame.entity, user_config)

        for i, result in enumerate(self.data):
            prompt += (" [{}. {}],".format(i + 1, ", ".join(["{}: {}".format(k,
                                              v) for k, v in result.items()])))
        prompt = prompt.strip(",") + ". "
        if self.frame.can_advance_results_list():
            prompt += ("there are also other results matching your criteria."
                      "  ask me to show you more if you want to see them. ")
        if self.frame.can_restore_results_list():
            prompt += ("if you want to see previous results, or the first "
                       "results of the list, just ask me.")

        return prompt.strip()

    def to_string_verbose(self):
        content = []
        for element in self.data:
            content.append("{" + ", ".join(["\"{}\": \"{}\"".format(k, v)                               \
                                      for k, v in element.items()]) + "}")

        return self.name + "[" + ", ".join(content) + "]"

    def run(self, belief):
        db = Database.get_instance()
        self.frame.result_set = db.kb_lookup(self.frame.table['table_name'],
                                                                    belief)
        self.data = self.frame.get_results_to_show()
        while self.frame.result_set and not self.data:
            self.frame.restore_results_list()
            self.data = self.frame.get_results_to_show()

        self.last_system_belief = belief
        
        return self

    def vui_dm_run(self):
        return templates.propose_run_template                                                           \
                .format(table_name=self.frame.table['table_name'],
                        slots=list(self.last_system_belief.keys()))

class Delete(CustomAction):

    def __init__(self, frame):
        table_name = frame.table['table_name']
        table_name = "".join([x.capitalize() for x in table_name.split("_")])
        name = "Delete{}".format(table_name)

        CustomAction.__init__(self, name, frame)

    def to_natural_language(self):
        prompt = ("i have registered your {} cancellation."
                             "").format(self.frame.entity)
        return prompt

    def to_string_verbose(self):
        content = self.frame.history[-1].items()
        return self.name + str({k : v for k, v in content if v is not None                              \
                                      and k in self.frame.get_all_slots()})

    def run(self):
        #db = Database.get_instance()
        #db.delete(self.frame.table['table_name'], 
        #     self.frame.get_results_to_show()[0])
        self.frame.result_set = []
        self.frame.update(dict.fromkeys(self.frame.content, None))
        self.slot_events = {'matches' : None, 'user_choice' : None}

        return self

    def vui_dm_run(self):
        return templates.delete_run_template                                                            \
                .format(table_name=self.frame.table['table_name'])

class Update(CustomAction):

    def __init__(self, frame):
        table_name = frame.table['table_name']
        table_name = "".join([x.capitalize() for x in table_name.split("_")])
        name = "Update{}".format(table_name)

        self.pk = db.column_to_slot(frame.table['pkey'], 
                              frame.table['table_name'])

        CustomAction.__init__(self, name, frame)

    def to_natural_language(self):
        prompt = ("your modifications to {} have been saved."
                               "").format(self.frame.entity)
        return prompt

    def to_string_verbose(self):
        content = self.frame.history[-1].items()
        return self.name + str({k : v for k, v in content if v is not None                              \
                                      and k in self.frame.get_all_slots()})

    def run(self):
        #db = Database.get_instance()
        #db.update(self.frame.table['table_name'], 
        #          self.frame.get_infod_content(),
        #                                 self.pk)

        self.frame.update(dict.fromkeys(self.frame.content, None))

        return self

    def vui_dm_run(self):
        return templates.update_run_template                                                            \
                .format(table_name=self.frame.table['table_name'],
                            slots=list(self.frame.content.keys()),
                                                   pkey=self.pkey)

class Insert(CustomAction):

    def __init__(self, frame):
        table_name = frame.table['table_name']
        table_name = "".join([x.capitalize() for x in table_name.split("_")])
        name = "Insert{}".format(table_name)

        CustomAction.__init__(self, name, frame)

    def to_natural_language(self):
        return "i have registered your {}.".format(self.frame.entity)

    def to_string_verbose(self):
        content = self.frame.history[-1].items()
        return self.name + str({k : v for k, v in content if v is not None                              \
                                      and k in self.frame.get_all_slots()})

    def run(self):
        #db = Database.get_instance()
        #db.insert(self.frame.table['table_name'],
        #          self.frame.get_infod_content())

        self.frame.update(dict.fromkeys(self.frame.content, None))

        return self

    def vui_dm_run(self):
        return templates.insert_run_template                                                            \
                .format(table_name=self.frame.table['table_name'],
                            slots=list(self.frame.content.keys()))

class Multichoice(CustomAction):

    def __init__(self, frame, slot):
        table_name = frame.table['table_name']
        table_name = "".join([x.capitalize() for x in table_name.split("_")])
        column_name = "".join([x.capitalize() for x in Database.get_instance()                          \
                                            .slot_to_column(slot).split("_")])
        name = "Multichoice{}{}".format(table_name, column_name)
        CustomAction.__init__(self, name, frame)
        self.target = slot

    def to_natural_language(self):
        options = ", ".join(sum([list(res.values()) for res in self.data], []))
        prompt = "you can choose between: {}".format(options)
        return prompt

    def to_string_verbose(self):
        content = []
        for element in self.data:
            content.append("{" + ", ".join(["\"{}\": \"{}\"".format(k, v)                               \
                                     for k, v in element.items()]) + "}")

        return self.name + "[" + ", ".join(content) + "]"

    def run(self, belief):
        db = Database.get_instance()
        self.data = db.project(self.frame.table['table_name'], 
                               self.frame.get_infod_content(),
                                                 self.target)
        if not self.data:
            self.data = db.project(self.frame.table['table_name'], 
                                                 {}, self.target)
        return self

    def vui_dm_run(self):
        return templates.multichoice_run_template                                                       \
                .format(table_name=self.frame.table['table_name'],
                            slots=list(self.frame.content.keys()),
                                              target=self.target)

class SaveChoice(CustomAction):

    def __init__(self, frame):
        table_name = frame.table['table_name']
        table_name = "".join([x.capitalize() for x in table_name.split("_")])
        name = "SaveChoice{}".format(table_name)

        CustomAction.__init__(self, name, frame)

    def to_natural_language(self):
        return "got it. let me save your preference."

    def to_string_verbose(self):
        content = (self.frame.history[-1].items() if self.frame.parent                                  \
                                      else self.frame.content.items())
        return self.name + "{" + ", ".join(["\"{}\": \"{}\"".format(k, v)                               \
                                              for k, v in content if k in                               \
                                              self.frame.get_all_slots()])                              \
                         + "}"                               

    def run(self):
        if len(self.frame.get_results_to_show()) > 1:
            raise ValueError("SaveChoice fired when result set has more than"
                             " one result: {}".format(self.frame.result_set))

        chosen = self.frame.get_results_to_show()[0]
        self.slot_events = {'user_choice' : None,
                            'matches' : None}

        self.frame.update(chosen)
        self.slot_events.update(chosen)
        self.frame.result_set = []

        return self

    def vui_dm_run(self):
        return templates.savechoice_run_template                                                        \
                .format(table_name=self.frame.table['table_name'])

class ResetDependencies(CustomAction):

    def __init__(self, frame):
        table_name = frame.table['table_name']
        table_name = "".join([x.capitalize() for x in table_name.split("_")])
        name = "ResetDependencies{}".format(table_name)

        CustomAction.__init__(self, name, frame)

    def to_natural_language(self):
        return "" # non-verbal action

    def to_string_verbose(self):
        dependencies = self.frame.dependencies
        old_cont = self.frame.history[-1]
        new_cont = self.frame.content
        changes = [s for s in self.frame.get_all_slots() if                                             \
                   old_cont[s] != new_cont[s] and old_cont[s]                                           \
                                                 is not None] 
        to_reset = []
        for slot in changes:
            for dep in dependencies.get(slot, []):
                if dep not in changes:
                    to_reset.append(dep)

        return self.name + "[" + ", ".join(to_reset) + "]"

    def run(self):
        dependencies = self.frame.dependencies
        old_cont = self.frame.history[-1]
        new_cont = self.frame.content
        changes = [s for s in self.frame.get_all_slots() if                                             \
                   old_cont[s] != new_cont[s] and old_cont[s]                                           \
                                                 is not None]
        self.slot_events = {}
        for slot in changes:
            for dep in dependencies.get(slot, []):
                if dep not in changes:
                    self.frame.content[dep] = None
                    self.slot_events[dep] = None

        return self

    def vui_dm_run(self):
        return templates.resetdependencies_run_template                                                 \
                .format(dependencies=self.frame.dependencies)

class Lookup(CustomAction):

    def __init__(self, frame):
        table_name = frame.table['table_name']
        table_name = "".join([x.capitalize() for x in table_name.split("_")])
        name = "Lookup{}".format(table_name)

        CustomAction.__init__(self, name, frame)

    def to_natural_language(self):
        if self.data:
            prompt = random.choice(["understood.", "alright.", "ok.", "got it."])
        else:
            user_config = " and ".join(["{}: {}".format(k, v) for k, v in                                   \
                                        self.last_system_belief.items()                                     \
                                        if k in self.frame.content                                          \
                                        .keys() and is_value(v)])
            
            prompt = ("unfortunately, i couldn't find any {} with {}"
                     ".").format(self.frame.entity, user_config)

        return prompt

    def to_string_verbose(self):
        return self.name + "_" + ("noResult" if not self.data else "ok")

    def run(self, belief):
        db = Database.get_instance()
        self.data = db.kb_lookup(self.frame.table['table_name'], belief)
        self.last_system_belief = belief

        self.slot_events = {}

        if not self.data:
            before  = self.frame.history[-1]
            current = self.frame.content
            self.slot_events = {k : None for k in current if                                            \
                                current[k] != before[k] and                                             \
                                     current[k] is not None}
        
        self.frame.update(self.slot_events)
        self.frame.clear_navigation_history()
        self.frame.result_set = self.data

        return self

    def vui_dm_run(self):
        return templates.lookup_run_template                                                            \
                .format(table_name=self.frame.table['table_name'],
                        slots=list(self.last_system_belief.keys()))

class PrepareForUpdates(CustomAction):

    def __init__(self, frame):
        table_name = frame.table['table_name']
        table_name = "".join([x.capitalize() for x in table_name.split("_")])
        name = "PrepareFor{}Updates".format(table_name)

        CustomAction.__init__(self, name, frame)

    def to_natural_language(self):
        pkey = Database.get_instance().column_to_slot(self.frame.table['pkey'],
                                                self.frame.table['table_name'])
        return "so you want to modify {} with id {}".format(self.frame.entity,
                                                     self.frame.content[pkey])

    def to_string_verbose(self):
        content = self.frame.content.items()
        return self.name + str({k : v for k, v in content if v is not None                              \
                                     and k in self.frame.get_all_slots()})

    def run(self):
        db = Database.get_instance()
        table_name = self.frame.table['table_name']
        #constraints = db.select_nth(self.frame.table['table_name'],
        #                            self.frame.get_infod_content(), 
        #                                                        1)
        constraints = self.frame.get_results_to_show()[0]
        pkey = db.column_to_slot(self.frame.table['pkey'],
                           self.frame.table['table_name'])

        self.frame.update(dict.fromkeys(self.frame.content, None))
        self.frame.content[pkey] = constraints[pkey]
        self.frame.result_set = []

        self.slot_events = dict.fromkeys(self.frame.content, None)
        self.slot_events.update({'pkey' : constraints[pkey],
                                 'user_choice' : None,
                                 'matches' : None})
        return self

    def vui_dm_run(self):
        return templates.prepareforupdates_run_template                                                 \
                .format(table_name=self.frame.table['table_name'],
                            slots=list(self.frame.content.keys()))

class RestorePreferences(CustomAction):

    def __init__(self, frame):
        table_name  = frame.table['table_name']
        parent_name = frame.parent.table['table_name']
        table_name  = "".join([x.capitalize() for x in table_name.split("_")])
        parent_name = "".join([x.capitalize() for x in parent_name.split("_")])
        name = "Restore{}PreferencesFrom{}".format(table_name, parent_name)

        CustomAction.__init__(self, name, frame)

    def to_natural_language(self):
        return "" # non-verbal action

    def to_string_verbose(self):
        return self.name + str({k : v for k, v in self.frame.content.items()                            \
                                                          if v is not None})

    def run(self, updates):
        self.frame.active = True

        cascade = []
        if not self.frame.parent.active:
            cascade += RestorePreferences(self.frame.parent).run({})

        db = Database.get_instance()
        table_name = self.frame.table['table_name'] 
        parent_name = self.frame.parent.table['table_name']
        pkey = db.column_to_slot(self.frame.table['pkey'], table_name)

        self.slot_events = {}

        for col in self.frame.parent.table['columns']:
            if col.get('refs', {}).get('table', "") == table_name:
                fkey = db.column_to_slot(col['column_name'], parent_name)
                preference_id = self.frame.parent.content[fkey]
                preference = {k : (v if k in self.frame.get_all_slots() else None) 
                                             for k, v in db.select_nth(table_name, 
                                               {pkey : preference_id}, 1).items()}
                for slot in updates.keys():
                    del preference[slot]
                    for dep in self.frame.dependencies.get(slot, []):
                        preference[dep] = None

                self.frame.parent.update({fkey : None})
                self.slot_events.update(preference)
                self.frame.update(preference)
                self.slot_events[fkey] = None

        self.frame.update(updates)
        cascade.append(self)
        return cascade

    def vui_dm_run(self):
        return templates.restorepreferences_run_template                                                \
                .format(parent_name=self.frame.parent.table['table_name'],
                                table_name=self.frame.table['table_name'],
                                    dependencies=self.frame.dependencies)

class TransferPreferences(CustomAction):

    def __init__(self, frame):
        table_name  = frame.table['table_name']
        parent_name = frame.parent.table['table_name']
        table_name  = "".join([x.capitalize() for x in table_name.split("_")])
        parent_name = "".join([x.capitalize() for x in parent_name.split("_")])
        name = "Transfer{}PreferencesTo{}".format(table_name, parent_name)

        CustomAction.__init__(self, name, frame)

    def to_natural_language(self):
        return "" # non-verbal action

    def to_string_verbose(self):
        fkey = None
        pkey = self.frame.table['pkey']
        parent_table = self.frame.parent.table

        for column in parent_table['columns']:
            if column.get('refs', {}).get('column', "") == pkey:
                db = Database.get_instance()
                fkey = db.column_to_slot(column['column_name'],
                                    parent_table['table_name'])
                break

        return self.name + str({fkey : self.frame.parent.content[fkey]})

    def run(self):
        db = Database.get_instance()
        table_name = self.frame.table['table_name']
        parent_name = self.frame.parent.table['table_name']
        pkey = db.column_to_slot(self.frame.table['pkey'], table_name)

        self.slot_events = {}

        for col in self.frame.parent.table['columns']:
            if col.get('refs', {}).get('table', "") == table_name:
                fkey = db.column_to_slot(col['column_name'], parent_name)
                self.frame.parent.update({fkey: self.frame.content[pkey]})
                self.slot_events[fkey] = self.frame.content[pkey]

        self.frame.update(dict.fromkeys(self.frame.content, None))
        self.slot_events.update(dict.fromkeys(self.frame.content, None))

        return self

    def vui_dm_run(self):
        return templates.transferpreferences_run_template                                               \
                .format(parent_name=self.frame.parent.table['table_name'],
                                table_name=self.frame.table['table_name'],
                                    slots=list(self.frame.content.keys()))


class RelaxLastRequest(CustomAction):

    def __init__(self, frame):
        name = "RelaxLastRequest"
        CustomAction.__init__(self, name, frame)

    def to_natural_language(self):
        return random.choice(["understood.", "ok.", "alright.", "got it."])

    def run(self):
        last_requested_slot = self.frame.get_next_slot()
        self.frame.update({last_requested_slot : DONT_CARE})
        self.slot_events = {last_requested_slot: DONT_CARE}
        return self

    def vui_dm_run(self):
        return templates.relaxlastrequest_run_template

class ReloadOptions(CustomAction):

    def __init__(self, frame):
        table_name = frame.table['table_name']
        table_name = "".join([x.capitalize() for x in table_name.split("_")])
        name = "Reload{}Options".format(table_name)

        CustomAction.__init__(self, name, frame)

    def to_natural_language(self):
        return "" # non-verbal action

    def run(self):
        relaxed_constraints = {k : (v if k in self.frame.get_all_slots() else                           \
                                None) for k, v in self.frame.content.items()}
        self.frame.update(relaxed_constraints)
        return self

    def vui_dm_run(self):
        return templates.reloadoptions_run_template                                                     \
                .format(unfeaturized_slots=[k for k in self.frame.content                               \
                         .keys() if k not in self.frame.get_all_slots()])

class BeginTask(CustomAction):

    def __init__(self, frame):
        table_name = frame.table['table_name']
        table_name = "".join([x.capitalize() for x in table_name.split("_")])
        name = "Begin{}{}Task".format(frame.subdialog.capitalize(), table_name)

        CustomAction.__init__(self, name, frame)

    def to_natural_language(self):
        task = "{} a {}".format(self.frame.subdialog.lower(), 
                self.frame.entity.lower().replace("_", r" "))
        
        return "ok, so you want to {}.".format(task)

    def run(self, frames):
        db = Database.get_instance()
        if hasattr(self.frame, 'result_set'):
            kb_seed = [[self.frame]]
            kb_seed[0].extend([f.table['table_name'] for f in                                           \
                                  frames if f != self.frame])
        else:
            kb_seed = []
            left = set([f for f in frames if f != self.frame])
            first_level = [f for f  in  frames  if                                                      \
                           f.parent == self.frame]

            for frame in first_level:
                kb_seed.append([frame])
                left.remove(frame)

            while left:
                for frame in [f for f in left]:
                    for kb in kb_seed:
                        if frame.parent in kb:
                            left.remove(frame)
                            kb.append(frame)
                        
        db.build_knowledge_base([[f.entity for f in seed_set]                                           \
                                    for seed_set in kb_seed])
        return self

    def vui_dm_run(self):
        return templates.begintask_run_template                                                         \
                .format(subdialog=self.frame.subdialog,
                        table_name=self.frame.table['table_name'],
                        kb_seed=Database.get_instance().get_kb_seed())


class CompleteTask(CustomAction):

    def __init__(self, frame):
        table_name = frame.table['table_name']
        table_name = "".join([x.capitalize() for x in table_name.split("_")])
        name = "Complete{}{}Task".format(frame.subdialog.capitalize(), table_name)

        CustomAction.__init__(self, name, frame)

    def to_natural_language(self):
        return ("now, is there anything else i can help you with,"
                                          " or should i finalize?")

    def run(self):
        self.slot_events = dict.fromkeys(self.frame.content, None)
        return self

    def vui_dm_run(self):
        return templates.completetask_run_template                                                      \
                .format(subdialog=self.frame.subdialog)

class Finalize(CustomAction):

    def __init__(self, frame):
        name = "Finalize"
        CustomAction.__init__(self, name, None)

    def to_natural_language(self):
        return "" # non-verbal action

    def run(self):
        return self

    def vui_dm_run(self):
        return templates.finalize_run_template

class LoadMoreOptions(CustomAction):

    def __init__(self, frame):
        name = "LoadMoreOptions"
        CustomAction.__init__(self, name, frame)

    def to_natural_language(self):
        if self.will_advance:
            return "alright, let me load more results."
        else:
            return "you have reached the end of the result list."

    def run(self):
        self.will_advance = self.frame.can_advance_results_list()
        self.frame.advance_results_list()
        return self

    def vui_dm_run(self):
        return templates.loadmoreoptions_run_template

class LoadPrevOptions(CustomAction):

    def __init__(self, frame):
        name = "LoadPrevOptions"
        CustomAction.__init__(self, name, frame)

    def to_natural_language(self):
        if self.will_restore:
            return "ok, let me load previous results."
        else:
            return "there are no previous results in your navigation history."

    def run(self):
        self.will_restore = self.frame.can_restore_results_list()
        self.frame.restore_results_list()
        return self

    def vui_dm_run(self):
        return templates.loadprevoptions_run_template

class LoadHeadOptions(CustomAction):

    def __init__(self, frame):
        name = "LoadHeadOptions"
        CustomAction.__init__(self, name, frame)

    def to_natural_language(self):
        return "gotcha, let me load the first options for you."

    def run(self):
        self.frame.to_results_list_head()
        return self

    def vui_dm_run(self):
        return templates.loadheadoptions_run_template