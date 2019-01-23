from database import Database
import random

"""

    Class modelling standard actions having just a name and not carrying any data

"""

class Action:
    
    def __init__(self, name, templates=[]):
        self.name, self.templates = name, templates

    def __str__(self):
        return self.to_string()
        
    def to_string(self):
        return self.name

"""

    These classes model actions that the agenda-based simulator needs to distinguish

"""
class MoreUpdates(Action):

    def __init__(self, entity, name="utter_ask_more_updates", templates=["Got it. Anything else you want to change?"]):
        Action.__init__(self, name, templates=templates)
        self.entity = entity

class PollUpdates(Action):

    def __init__(self, entity, name="utter_ask_for_updates", templates=["Now then, what would you like to change?"]):
        Action.__init__(self, name, templates=templates)
        self.entity = entity

class Acknowledge(Action):

    def __init__(self, name="acknowledge", templates=["Alright", "Got it", "Ok"]):
        Action.__init__(self, name, templates=templates)

class Request(Action):

    def __init__(self, slot, entity, name="utter_ask", templates=["Which ", "Please tell me the "]):
        db = Database.get_instance()
        Action.__init__(self, name, templates=[t + "{}'s {}".format(db.slot_to_table(slot), 
                                               db.slot_to_column(slot)) for t in templates])
        self.slot = slot
        self.entity = entity

    def to_string(self):
        return self.name + "_" + self.slot

class Greet(Action):

    def __init__(self, name="utter_ask_howcanhelp", templates=["Hello, how can I help you?"]):
        Action.__init__(self, name, templates=templates)

class Bye(Action):

    def __init__(self, name="utter_bye", templates=["Goodbye"]):
        Action.__init__(self, name, templates=templates)