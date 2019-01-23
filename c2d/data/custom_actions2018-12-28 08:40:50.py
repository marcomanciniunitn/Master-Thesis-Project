from database import Database

Database.get_instance(database="mysql://root:root@localhost:3306/movies")

from rasa_core.actions import Action

class MultichoiceTicketPurchaseNumberOfTickets(Action):

    def name(self):
        return "MultichoiceTicketPurchaseNumberOfTickets"

    def run(self, dispatcher, tracker, domain):        
        from database import Database, is_value
        db = Database.get_instance() 

        slots  = {'ticket_purchase::customer_name', 'screening::fk_movie', 'screening::date', 'movie::rating', 'screening::fk_theater', 'screening::time', 'theater::name', 'theater::city', 'movie::genre', 'movie::actor', 'movie::title', 'movie::director', 'ticket_purchase::number_of_tickets', 'theater::chain', 'ticket_purchase::number_of_kids', 'ticket_purchase::fk_screening'}
        target = "ticket_purchase::number_of_tickets"
        user_config = {s : tracker.get_slot(s) for s in slots}
        
        results = db.kb_lookup("ticket_purchase", user_config)

        if not results:
            results = db.project("ticket_purchase", {}, target)
            if not results:
                from rasa_core.events import UserUtteranceReverted
                return [UserUtteranceReverted()]

        _results = set()
        for row in results:
            _results.add(row[target])

        options = ", ".join(list(_results)[:5])
        if len(_results) > 5:
            options += " and more"

        dispatcher.utter_message("You can choose among the following {}s:"
                                 " {}".format(db.slot_to_column(target), 
                                 options).replace("_", " "))
        
        from rasa_core.events import SlotSet
        return []

        
class MultichoiceTicketPurchaseNumberOfKids(Action):

    def name(self):
        return "MultichoiceTicketPurchaseNumberOfKids"

    def run(self, dispatcher, tracker, domain):        
        from database import Database, is_value
        db = Database.get_instance() 

        slots  = {'ticket_purchase::customer_name', 'screening::fk_movie', 'screening::date', 'movie::rating', 'screening::fk_theater', 'screening::time', 'theater::name', 'theater::city', 'movie::genre', 'movie::actor', 'movie::title', 'movie::director', 'ticket_purchase::number_of_tickets', 'theater::chain', 'ticket_purchase::number_of_kids', 'ticket_purchase::fk_screening'}
        target = "ticket_purchase::number_of_kids"
        user_config = {s : tracker.get_slot(s) for s in slots}
        
        results = db.kb_lookup("ticket_purchase", user_config)

        if not results:
            results = db.project("ticket_purchase", {}, target)
            if not results:
                from rasa_core.events import UserUtteranceReverted
                return [UserUtteranceReverted()]

        _results = set()
        for row in results:
            _results.add(row[target])

        options = ", ".join(list(_results)[:5])
        if len(_results) > 5:
            options += " and more"

        dispatcher.utter_message("You can choose among the following {}s:"
                                 " {}".format(db.slot_to_column(target), 
                                 options).replace("_", " "))
        
        from rasa_core.events import SlotSet
        return []

        
class MultichoiceTicketPurchaseCustomerName(Action):

    def name(self):
        return "MultichoiceTicketPurchaseCustomerName"

    def run(self, dispatcher, tracker, domain):        
        from database import Database, is_value
        db = Database.get_instance() 

        slots  = {'ticket_purchase::customer_name', 'screening::fk_movie', 'screening::date', 'movie::rating', 'screening::fk_theater', 'screening::time', 'theater::name', 'theater::city', 'movie::genre', 'movie::actor', 'movie::title', 'movie::director', 'ticket_purchase::number_of_tickets', 'theater::chain', 'ticket_purchase::number_of_kids', 'ticket_purchase::fk_screening'}
        target = "ticket_purchase::customer_name"
        user_config = {s : tracker.get_slot(s) for s in slots}
        
        results = db.kb_lookup("ticket_purchase", user_config)

        if not results:
            results = db.project("ticket_purchase", {}, target)
            if not results:
                from rasa_core.events import UserUtteranceReverted
                return [UserUtteranceReverted()]

        _results = set()
        for row in results:
            _results.add(row[target])

        options = ", ".join(list(_results)[:5])
        if len(_results) > 5:
            options += " and more"

        dispatcher.utter_message("You can choose among the following {}s:"
                                 " {}".format(db.slot_to_column(target), 
                                 options).replace("_", " "))
        
        from rasa_core.events import SlotSet
        return []

        
class MultichoiceScreeningTime(Action):

    def name(self):
        return "MultichoiceScreeningTime"

    def run(self, dispatcher, tracker, domain):        
        from database import Database, is_value
        db = Database.get_instance() 

        slots  = {'ticket_purchase::customer_name', 'screening::fk_movie', 'screening::date', 'movie::rating', 'screening::fk_theater', 'screening::time', 'theater::name', 'theater::city', 'movie::genre', 'movie::actor', 'movie::title', 'movie::director', 'ticket_purchase::number_of_tickets', 'theater::chain', 'ticket_purchase::number_of_kids', 'ticket_purchase::fk_screening'}
        target = "screening::time"
        user_config = {s : tracker.get_slot(s) for s in slots}
        
        results = db.kb_lookup("screening", user_config)

        if not results:
            results = db.project("screening", {}, target)
            if not results:
                from rasa_core.events import UserUtteranceReverted
                return [UserUtteranceReverted()]

        _results = set()
        for row in results:
            _results.add(row[target])

        options = ", ".join(list(_results)[:5])
        if len(_results) > 5:
            options += " and more"

        dispatcher.utter_message("You can choose among the following {}s:"
                                 " {}".format(db.slot_to_column(target), 
                                 options).replace("_", " "))
        
        from rasa_core.events import SlotSet
        return []

        
class MultichoiceScreeningDate(Action):

    def name(self):
        return "MultichoiceScreeningDate"

    def run(self, dispatcher, tracker, domain):        
        from database import Database, is_value
        db = Database.get_instance() 

        slots  = {'ticket_purchase::customer_name', 'screening::fk_movie', 'screening::date', 'movie::rating', 'screening::fk_theater', 'screening::time', 'theater::name', 'theater::city', 'movie::genre', 'movie::actor', 'movie::title', 'movie::director', 'ticket_purchase::number_of_tickets', 'theater::chain', 'ticket_purchase::number_of_kids', 'ticket_purchase::fk_screening'}
        target = "screening::date"
        user_config = {s : tracker.get_slot(s) for s in slots}
        
        results = db.kb_lookup("screening", user_config)

        if not results:
            results = db.project("screening", {}, target)
            if not results:
                from rasa_core.events import UserUtteranceReverted
                return [UserUtteranceReverted()]

        _results = set()
        for row in results:
            _results.add(row[target])

        options = ", ".join(list(_results)[:5])
        if len(_results) > 5:
            options += " and more"

        dispatcher.utter_message("You can choose among the following {}s:"
                                 " {}".format(db.slot_to_column(target), 
                                 options).replace("_", " "))
        
        from rasa_core.events import SlotSet
        return []

        
class AnswerQuestionAboutScreeningPrice(Action):

    def name(self):
        return "AnswerQuestionAboutScreeningPrice"

    def run(self, dispatcher, tracker, domain):        
        matches = tracker.get_slot("matches")
        choice  = tracker.get_slot("user_choice")

        from rasa_core.events import LastUtteranceReverted
        if not matches:
            dispatcher.utter_message("Sorry, I didn't catch that")
            return [LastUtteranceReverted()]

        slot  = "screening::price"
        feats = ['screening::time', 'screening::date']
        from database import Database, ordinal_index_to_int
        db     = Database.get_instance()
        column = db.slot_to_column(slot)
        table  = db.slot_to_table(slot)

        if choice is not None:
            if ordinal_index_to_int(choice):
                chosen = matches[int(choice)-1]
            else:
                dispatcher.utter_message("Sorry, I didn't catch that.")
                from rasa_core.events import SlotSet
                return [SlotSet("user_choice", None)]
        else:
            chosen = matches[0]

        formatted_chosen = ", ".join(["{}: {}".format(db.slot_to_column(k).replace("_", " "),
                            v) for k, v in db.remove_fkeys_from_result_set(chosen).items() if k         \
                            in feats])

        dispatcher.utter_message("The {} [{}] {} is the following: {}"
                                 "".format(table, formatted_chosen, slot, chosen[slot])                 \
                                 .replace("_", " "))

        from rasa_core.events import SlotSet
        events = [SlotSet("matches", [chosen]), 
                  SlotSet("user_choice", None)]
        
        for k in chosen.keys():
            events.append(SlotSet(k, chosen[k]))

        return events

class AnswerQuestionAboutScreeningRoom(Action):

    def name(self):
        return "AnswerQuestionAboutScreeningRoom"

    def run(self, dispatcher, tracker, domain):        
        matches = tracker.get_slot("matches")
        choice  = tracker.get_slot("user_choice")

        from rasa_core.events import LastUtteranceReverted
        if not matches:
            dispatcher.utter_message("Sorry, I didn't catch that")
            return [LastUtteranceReverted()]

        slot  = "screening::room"
        feats = ['screening::time', 'screening::date']
        from database import Database, ordinal_index_to_int
        db     = Database.get_instance()
        column = db.slot_to_column(slot)
        table  = db.slot_to_table(slot)

        if choice is not None:
            if ordinal_index_to_int(choice):
                chosen = matches[int(choice)-1]
            else:
                dispatcher.utter_message("Sorry, I didn't catch that.")
                from rasa_core.events import SlotSet
                return [SlotSet("user_choice", None)]
        else:
            chosen = matches[0]

        formatted_chosen = ", ".join(["{}: {}".format(db.slot_to_column(k).replace("_", " "),
                            v) for k, v in db.remove_fkeys_from_result_set(chosen).items() if k         \
                            in feats])

        dispatcher.utter_message("The {} [{}] {} is the following: {}"
                                 "".format(table, formatted_chosen, slot, chosen[slot])                 \
                                 .replace("_", " "))

        from rasa_core.events import SlotSet
        events = [SlotSet("matches", [chosen]), 
                  SlotSet("user_choice", None)]
        
        for k in chosen.keys():
            events.append(SlotSet(k, chosen[k]))

        return events

class MultichoiceMovieTitle(Action):

    def name(self):
        return "MultichoiceMovieTitle"

    def run(self, dispatcher, tracker, domain):        
        from database import Database, is_value
        db = Database.get_instance() 

        slots  = {'ticket_purchase::customer_name', 'screening::fk_movie', 'screening::date', 'movie::rating', 'screening::fk_theater', 'screening::time', 'theater::name', 'theater::city', 'movie::genre', 'movie::actor', 'movie::title', 'movie::director', 'ticket_purchase::number_of_tickets', 'theater::chain', 'ticket_purchase::number_of_kids', 'ticket_purchase::fk_screening'}
        target = "movie::title"
        user_config = {s : tracker.get_slot(s) for s in slots}
        
        results = db.kb_lookup("movie", user_config)

        if not results:
            results = db.project("movie", {}, target)
            if not results:
                from rasa_core.events import UserUtteranceReverted
                return [UserUtteranceReverted()]

        _results = set()
        for row in results:
            _results.add(row[target])

        options = ", ".join(list(_results)[:5])
        if len(_results) > 5:
            options += " and more"

        dispatcher.utter_message("You can choose among the following {}s:"
                                 " {}".format(db.slot_to_column(target), 
                                 options).replace("_", " "))
        
        from rasa_core.events import SlotSet
        return []

        
class MultichoiceMovieActor(Action):

    def name(self):
        return "MultichoiceMovieActor"

    def run(self, dispatcher, tracker, domain):        
        from database import Database, is_value
        db = Database.get_instance() 

        slots  = {'ticket_purchase::customer_name', 'screening::fk_movie', 'screening::date', 'movie::rating', 'screening::fk_theater', 'screening::time', 'theater::name', 'theater::city', 'movie::genre', 'movie::actor', 'movie::title', 'movie::director', 'ticket_purchase::number_of_tickets', 'theater::chain', 'ticket_purchase::number_of_kids', 'ticket_purchase::fk_screening'}
        target = "movie::actor"
        user_config = {s : tracker.get_slot(s) for s in slots}
        
        results = db.kb_lookup("movie", user_config)

        if not results:
            results = db.project("movie", {}, target)
            if not results:
                from rasa_core.events import UserUtteranceReverted
                return [UserUtteranceReverted()]

        _results = set()
        for row in results:
            _results.add(row[target])

        options = ", ".join(list(_results)[:5])
        if len(_results) > 5:
            options += " and more"

        dispatcher.utter_message("You can choose among the following {}s:"
                                 " {}".format(db.slot_to_column(target), 
                                 options).replace("_", " "))
        
        from rasa_core.events import SlotSet
        return []

        
class MultichoiceMovieRating(Action):

    def name(self):
        return "MultichoiceMovieRating"

    def run(self, dispatcher, tracker, domain):        
        from database import Database, is_value
        db = Database.get_instance() 

        slots  = {'ticket_purchase::customer_name', 'screening::fk_movie', 'screening::date', 'movie::rating', 'screening::fk_theater', 'screening::time', 'theater::name', 'theater::city', 'movie::genre', 'movie::actor', 'movie::title', 'movie::director', 'ticket_purchase::number_of_tickets', 'theater::chain', 'ticket_purchase::number_of_kids', 'ticket_purchase::fk_screening'}
        target = "movie::rating"
        user_config = {s : tracker.get_slot(s) for s in slots}
        
        results = db.kb_lookup("movie", user_config)

        if not results:
            results = db.project("movie", {}, target)
            if not results:
                from rasa_core.events import UserUtteranceReverted
                return [UserUtteranceReverted()]

        _results = set()
        for row in results:
            _results.add(row[target])

        options = ", ".join(list(_results)[:5])
        if len(_results) > 5:
            options += " and more"

        dispatcher.utter_message("You can choose among the following {}s:"
                                 " {}".format(db.slot_to_column(target), 
                                 options).replace("_", " "))
        
        from rasa_core.events import SlotSet
        return []

        
class MultichoiceMovieGenre(Action):

    def name(self):
        return "MultichoiceMovieGenre"

    def run(self, dispatcher, tracker, domain):        
        from database import Database, is_value
        db = Database.get_instance() 

        slots  = {'ticket_purchase::customer_name', 'screening::fk_movie', 'screening::date', 'movie::rating', 'screening::fk_theater', 'screening::time', 'theater::name', 'theater::city', 'movie::genre', 'movie::actor', 'movie::title', 'movie::director', 'ticket_purchase::number_of_tickets', 'theater::chain', 'ticket_purchase::number_of_kids', 'ticket_purchase::fk_screening'}
        target = "movie::genre"
        user_config = {s : tracker.get_slot(s) for s in slots}
        
        results = db.kb_lookup("movie", user_config)

        if not results:
            results = db.project("movie", {}, target)
            if not results:
                from rasa_core.events import UserUtteranceReverted
                return [UserUtteranceReverted()]

        _results = set()
        for row in results:
            _results.add(row[target])

        options = ", ".join(list(_results)[:5])
        if len(_results) > 5:
            options += " and more"

        dispatcher.utter_message("You can choose among the following {}s:"
                                 " {}".format(db.slot_to_column(target), 
                                 options).replace("_", " "))
        
        from rasa_core.events import SlotSet
        return []

        
class MultichoiceMovieDirector(Action):

    def name(self):
        return "MultichoiceMovieDirector"

    def run(self, dispatcher, tracker, domain):        
        from database import Database, is_value
        db = Database.get_instance() 

        slots  = {'ticket_purchase::customer_name', 'screening::fk_movie', 'screening::date', 'movie::rating', 'screening::fk_theater', 'screening::time', 'theater::name', 'theater::city', 'movie::genre', 'movie::actor', 'movie::title', 'movie::director', 'ticket_purchase::number_of_tickets', 'theater::chain', 'ticket_purchase::number_of_kids', 'ticket_purchase::fk_screening'}
        target = "movie::director"
        user_config = {s : tracker.get_slot(s) for s in slots}
        
        results = db.kb_lookup("movie", user_config)

        if not results:
            results = db.project("movie", {}, target)
            if not results:
                from rasa_core.events import UserUtteranceReverted
                return [UserUtteranceReverted()]

        _results = set()
        for row in results:
            _results.add(row[target])

        options = ", ".join(list(_results)[:5])
        if len(_results) > 5:
            options += " and more"

        dispatcher.utter_message("You can choose among the following {}s:"
                                 " {}".format(db.slot_to_column(target), 
                                 options).replace("_", " "))
        
        from rasa_core.events import SlotSet
        return []

        
class AnswerQuestionAboutMoviePlot(Action):

    def name(self):
        return "AnswerQuestionAboutMoviePlot"

    def run(self, dispatcher, tracker, domain):        
        matches = tracker.get_slot("matches")
        choice  = tracker.get_slot("user_choice")

        from rasa_core.events import LastUtteranceReverted
        if not matches:
            dispatcher.utter_message("Sorry, I didn't catch that")
            return [LastUtteranceReverted()]

        slot  = "movie::plot"
        feats = ['movie::title', 'movie::actor', 'movie::rating', 'movie::genre', 'movie::director']
        from database import Database, ordinal_index_to_int
        db     = Database.get_instance()
        column = db.slot_to_column(slot)
        table  = db.slot_to_table(slot)

        if choice is not None:
            if ordinal_index_to_int(choice):
                chosen = matches[int(choice)-1]
            else:
                dispatcher.utter_message("Sorry, I didn't catch that.")
                from rasa_core.events import SlotSet
                return [SlotSet("user_choice", None)]
        else:
            chosen = matches[0]

        formatted_chosen = ", ".join(["{}: {}".format(db.slot_to_column(k).replace("_", " "),
                            v) for k, v in db.remove_fkeys_from_result_set(chosen).items() if k         \
                            in feats])

        dispatcher.utter_message("The {} [{}] {} is the following: {}"
                                 "".format(table, formatted_chosen, slot, chosen[slot])                 \
                                 .replace("_", " "))

        from rasa_core.events import SlotSet
        events = [SlotSet("matches", [chosen]), 
                  SlotSet("user_choice", None)]
        
        for k in chosen.keys():
            events.append(SlotSet(k, chosen[k]))

        return events

class AnswerQuestionAboutMovieCast(Action):

    def name(self):
        return "AnswerQuestionAboutMovieCast"

    def run(self, dispatcher, tracker, domain):        
        matches = tracker.get_slot("matches")
        choice  = tracker.get_slot("user_choice")

        from rasa_core.events import LastUtteranceReverted
        if not matches:
            dispatcher.utter_message("Sorry, I didn't catch that")
            return [LastUtteranceReverted()]

        slot  = "movie::cast"
        feats = ['movie::title', 'movie::actor', 'movie::rating', 'movie::genre', 'movie::director']
        from database import Database, ordinal_index_to_int
        db     = Database.get_instance()
        column = db.slot_to_column(slot)
        table  = db.slot_to_table(slot)

        if choice is not None:
            if ordinal_index_to_int(choice):
                chosen = matches[int(choice)-1]
            else:
                dispatcher.utter_message("Sorry, I didn't catch that.")
                from rasa_core.events import SlotSet
                return [SlotSet("user_choice", None)]
        else:
            chosen = matches[0]

        formatted_chosen = ", ".join(["{}: {}".format(db.slot_to_column(k).replace("_", " "),
                            v) for k, v in db.remove_fkeys_from_result_set(chosen).items() if k         \
                            in feats])

        dispatcher.utter_message("The {} [{}] {} is the following: {}"
                                 "".format(table, formatted_chosen, slot, chosen[slot])                 \
                                 .replace("_", " "))

        from rasa_core.events import SlotSet
        events = [SlotSet("matches", [chosen]), 
                  SlotSet("user_choice", None)]
        
        for k in chosen.keys():
            events.append(SlotSet(k, chosen[k]))

        return events

class MultichoiceTheaterName(Action):

    def name(self):
        return "MultichoiceTheaterName"

    def run(self, dispatcher, tracker, domain):        
        from database import Database, is_value
        db = Database.get_instance() 

        slots  = {'ticket_purchase::customer_name', 'screening::fk_movie', 'screening::date', 'movie::rating', 'screening::fk_theater', 'screening::time', 'theater::name', 'theater::city', 'movie::genre', 'movie::actor', 'movie::title', 'movie::director', 'ticket_purchase::number_of_tickets', 'theater::chain', 'ticket_purchase::number_of_kids', 'ticket_purchase::fk_screening'}
        target = "theater::name"
        user_config = {s : tracker.get_slot(s) for s in slots}
        
        results = db.kb_lookup("theater", user_config)

        if not results:
            results = db.project("theater", {}, target)
            if not results:
                from rasa_core.events import UserUtteranceReverted
                return [UserUtteranceReverted()]

        _results = set()
        for row in results:
            _results.add(row[target])

        options = ", ".join(list(_results)[:5])
        if len(_results) > 5:
            options += " and more"

        dispatcher.utter_message("You can choose among the following {}s:"
                                 " {}".format(db.slot_to_column(target), 
                                 options).replace("_", " "))
        
        from rasa_core.events import SlotSet
        return []

        
class MultichoiceTheaterCity(Action):

    def name(self):
        return "MultichoiceTheaterCity"

    def run(self, dispatcher, tracker, domain):        
        from database import Database, is_value
        db = Database.get_instance() 

        slots  = {'ticket_purchase::customer_name', 'screening::fk_movie', 'screening::date', 'movie::rating', 'screening::fk_theater', 'screening::time', 'theater::name', 'theater::city', 'movie::genre', 'movie::actor', 'movie::title', 'movie::director', 'ticket_purchase::number_of_tickets', 'theater::chain', 'ticket_purchase::number_of_kids', 'ticket_purchase::fk_screening'}
        target = "theater::city"
        user_config = {s : tracker.get_slot(s) for s in slots}
        
        results = db.kb_lookup("theater", user_config)

        if not results:
            results = db.project("theater", {}, target)
            if not results:
                from rasa_core.events import UserUtteranceReverted
                return [UserUtteranceReverted()]

        _results = set()
        for row in results:
            _results.add(row[target])

        options = ", ".join(list(_results)[:5])
        if len(_results) > 5:
            options += " and more"

        dispatcher.utter_message("You can choose among the following {}s:"
                                 " {}".format(db.slot_to_column(target), 
                                 options).replace("_", " "))
        
        from rasa_core.events import SlotSet
        return []

        
class MultichoiceTheaterChain(Action):

    def name(self):
        return "MultichoiceTheaterChain"

    def run(self, dispatcher, tracker, domain):        
        from database import Database, is_value
        db = Database.get_instance() 

        slots  = {'ticket_purchase::customer_name', 'screening::fk_movie', 'screening::date', 'movie::rating', 'screening::fk_theater', 'screening::time', 'theater::name', 'theater::city', 'movie::genre', 'movie::actor', 'movie::title', 'movie::director', 'ticket_purchase::number_of_tickets', 'theater::chain', 'ticket_purchase::number_of_kids', 'ticket_purchase::fk_screening'}
        target = "theater::chain"
        user_config = {s : tracker.get_slot(s) for s in slots}
        
        results = db.kb_lookup("theater", user_config)

        if not results:
            results = db.project("theater", {}, target)
            if not results:
                from rasa_core.events import UserUtteranceReverted
                return [UserUtteranceReverted()]

        _results = set()
        for row in results:
            _results.add(row[target])

        options = ", ".join(list(_results)[:5])
        if len(_results) > 5:
            options += " and more"

        dispatcher.utter_message("You can choose among the following {}s:"
                                 " {}".format(db.slot_to_column(target), 
                                 options).replace("_", " "))
        
        from rasa_core.events import SlotSet
        return []

        
class AnswerQuestionAboutTheaterAddress(Action):

    def name(self):
        return "AnswerQuestionAboutTheaterAddress"

    def run(self, dispatcher, tracker, domain):        
        matches = tracker.get_slot("matches")
        choice  = tracker.get_slot("user_choice")

        from rasa_core.events import LastUtteranceReverted
        if not matches:
            dispatcher.utter_message("Sorry, I didn't catch that")
            return [LastUtteranceReverted()]

        slot  = "theater::address"
        feats = ['theater::name', 'theater::city', 'theater::chain']
        from database import Database, ordinal_index_to_int
        db     = Database.get_instance()
        column = db.slot_to_column(slot)
        table  = db.slot_to_table(slot)

        if choice is not None:
            if ordinal_index_to_int(choice):
                chosen = matches[int(choice)-1]
            else:
                dispatcher.utter_message("Sorry, I didn't catch that.")
                from rasa_core.events import SlotSet
                return [SlotSet("user_choice", None)]
        else:
            chosen = matches[0]

        formatted_chosen = ", ".join(["{}: {}".format(db.slot_to_column(k).replace("_", " "),
                            v) for k, v in db.remove_fkeys_from_result_set(chosen).items() if k         \
                            in feats])

        dispatcher.utter_message("The {} [{}] {} is the following: {}"
                                 "".format(table, formatted_chosen, slot, chosen[slot])                 \
                                 .replace("_", " "))

        from rasa_core.events import SlotSet
        events = [SlotSet("matches", [chosen]), 
                  SlotSet("user_choice", None)]
        
        for k in chosen.keys():
            events.append(SlotSet(k, chosen[k]))

        return events

class BeginInsertTicketPurchaseTask(Action):

    def name(self):
        return "BeginInsertTicketPurchaseTask"

    def run(self, dispatcher, tracker, domain):        
        from database import Database
        from rasa_core.events import SlotSet
        db = Database.get_instance().build_knowledge_base([['screening', 'movie', 'theater']])
        dispatcher.utter_message("Alright. So you want to insert"
                                 " a ticket_purchase".replace("_", " "))
        return [SlotSet("queries", []),
                SlotSet("results_offsets", [0]),
                SlotSet("results_displayed", 3)]

        
class ResetDependenciesTheater(Action):

    def name(self):
        return "ResetDependenciesTheater"

    def run(self, dispatcher, tracker, domain):        
        dependencies = {'theater::city': ['theater::chain', 'theater::name'], 'theater::chain': ['theater::city', 'theater::name'], 'theater::name': ['theater::city', 'theater::chain']}
        from rasa_core.utils.state_history import StateHistory
        updated = StateHistory().get_updated_slots(tracker)

        from database import DONT_CARE
        ignore   = [k for k in updated.keys() if updated[k] == DONT_CARE]
        to_check = [k for k in updated.keys() if k not in ignore]

        from rasa_core.events import SlotSet

        resets = []
        for k in to_check:
            for dep in dependencies.get(k, []):
                if dep not in updated.keys():
                    resets.append(SlotSet(dep, None))
        
        return resets
        
        
class LookupTheater(Action):

    def name(self):
        return "LookupTheater"

    def run(self, dispatcher, tracker, domain):        
        from database import Database, is_value
        slots = ['ticket_purchase::id', 'ticket_purchase::number_of_kids', 'ticket_purchase::number_of_tickets', 'ticket_purchase::customer_name', 'ticket_purchase::fk_screening', 'screening::id', 'screening::time', 'screening::date', 'screening::price', 'screening::room', 'screening::fk_movie', 'screening::fk_theater', 'movie::id', 'movie::title', 'movie::genre', 'movie::director', 'movie::plot', 'movie::actor', 'movie::rating', 'movie::cast', 'theater::id', 'theater::name', 'theater::chain', 'theater::city', 'theater::address']
        db = Database.get_instance() 
        matches = db.kb_lookup("theater", {s : tracker.get_slot(s)                                \
                                                       for s in slots})
        from rasa_core.utils.state_history import StateHistory
        from rasa_core.events import SlotSet
        if not matches:
            last_set_slots = StateHistory().get_events(tracker, 
                             event_type='user')[-1]['parse_data']['entities']
            
            configuration = db.remove_fkeys_from_result_set({s :                                       \
                            tracker.get_slot(s) for s in slots if                                       \
                            is_value(tracker.get_slot(s))})
            configuration = " and ".join(["{} {}".format(db.slot_to_column(k), v)                   \
                             for k, v in configuration.items()])
            
            dispatcher.utter_message("Unfortunately, I couldn't find any"
                                     " theater with {}".format(configuration)                    \
                                     .replace("_", " "))

            return [SlotSet(e['entity'], None) for e in last_set_slots]
            
        import random
        prompts = ["Alright, got that", "Understood", "Mm-mmh"]
        dispatcher.utter_message(random.choice(prompts).replace("_", " "))

        return [SlotSet("matches", matches), SlotSet("results_offsets", [0])]

        
class ResetDependenciesMovie(Action):

    def name(self):
        return "ResetDependenciesMovie"

    def run(self, dispatcher, tracker, domain):        
        dependencies = {'movie::director': ['movie::actor', 'movie::rating', 'movie::genre', 'movie::title'], 'movie::title': ['movie::actor', 'movie::director', 'movie::genre', 'movie::rating'], 'movie::genre': ['movie::actor', 'movie::director', 'movie::title'], 'movie::actor': ['movie::rating', 'movie::genre', 'movie::title', 'movie::director'], 'movie::rating': ['movie::actor', 'movie::director', 'movie::title']}
        from rasa_core.utils.state_history import StateHistory
        updated = StateHistory().get_updated_slots(tracker)

        from database import DONT_CARE
        ignore   = [k for k in updated.keys() if updated[k] == DONT_CARE]
        to_check = [k for k in updated.keys() if k not in ignore]

        from rasa_core.events import SlotSet

        resets = []
        for k in to_check:
            for dep in dependencies.get(k, []):
                if dep not in updated.keys():
                    resets.append(SlotSet(dep, None))
        
        return resets
        
        
class LookupMovie(Action):

    def name(self):
        return "LookupMovie"

    def run(self, dispatcher, tracker, domain):        
        from database import Database, is_value
        slots = ['ticket_purchase::id', 'ticket_purchase::number_of_kids', 'ticket_purchase::number_of_tickets', 'ticket_purchase::customer_name', 'ticket_purchase::fk_screening', 'screening::id', 'screening::time', 'screening::date', 'screening::price', 'screening::room', 'screening::fk_movie', 'screening::fk_theater', 'movie::id', 'movie::title', 'movie::genre', 'movie::director', 'movie::plot', 'movie::actor', 'movie::rating', 'movie::cast', 'theater::id', 'theater::name', 'theater::chain', 'theater::city', 'theater::address']
        db = Database.get_instance() 
        matches = db.kb_lookup("movie", {s : tracker.get_slot(s)                                \
                                                       for s in slots})
        from rasa_core.utils.state_history import StateHistory
        from rasa_core.events import SlotSet
        if not matches:
            last_set_slots = StateHistory().get_events(tracker, 
                             event_type='user')[-1]['parse_data']['entities']
            
            configuration = db.remove_fkeys_from_result_set({s :                                       \
                            tracker.get_slot(s) for s in slots if                                       \
                            is_value(tracker.get_slot(s))})
            configuration = " and ".join(["{} {}".format(db.slot_to_column(k), v)                   \
                             for k, v in configuration.items()])
            
            dispatcher.utter_message("Unfortunately, I couldn't find any"
                                     " movie with {}".format(configuration)                    \
                                     .replace("_", " "))

            return [SlotSet(e['entity'], None) for e in last_set_slots]
            
        import random
        prompts = ["Alright, got that", "Understood", "Mm-mmh"]
        dispatcher.utter_message(random.choice(prompts).replace("_", " "))

        return [SlotSet("matches", matches), SlotSet("results_offsets", [0])]

        
class ProposeMovie(Action):

    def name(self):
        return "ProposeMovie"

    def run(self, dispatcher, tracker, domain):        
        slots = ['ticket_purchase::id', 'ticket_purchase::number_of_kids', 'ticket_purchase::number_of_tickets', 'ticket_purchase::customer_name', 'ticket_purchase::fk_screening', 'screening::id', 'screening::time', 'screening::date', 'screening::price', 'screening::room', 'screening::fk_movie', 'screening::fk_theater', 'movie::id', 'movie::title', 'movie::genre', 'movie::director', 'movie::plot', 'movie::actor', 'movie::rating', 'movie::cast', 'theater::id', 'theater::name', 'theater::chain', 'theater::city', 'theater::address']
        feats = ['movie::title', 'movie::actor', 'movie::rating', 'movie::genre', 'movie::director']

        from database import Database, is_value, ordinal_index_to_int
        db = Database.get_instance() 
        matches = tracker.get_slot("matches")

        if matches is None:
            matches = matches if matches else db.kb_lookup("movie",
                                {s : tracker.get_slot(s) for s in slots})
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
            if user_choice and ordinal_index_to_int(user_choice):
                rows = [rows[ordinal_index_to_int(user_choice) - 1]]
                events.append(SlotSet("results_offsets", [0]))
             
            if len(rows) == 1:
                message = "Is this movie what you were" +                                        \
                                               " looking for?"
            else:
                user_config = {s : tracker.get_slot(s) for s in slots}
                user_config = {db.slot_to_column(k) : v for k, v in db                                 \
                                .remove_fkeys_from_result_set(user_config)
                                .items() if is_value(v)}

                message = "There are more than one movie with "   +                              \
                          "{}. Here, let me show you:".format((" and " +                              \
                          "").join(["{} {}".format(k, v) for k, v in                                \
                          user_config.items()]))
            
            dispatcher.utter_message(message.replace("_", " "))
            for i, row in enumerate(rows):
                row = db.remove_fkeys_from_result_set(row)
                formatted_option = ", ".join(["{}: {}".format(db.slot_to_column(k),
                                    v) for k, v in row.items() if k in feats])

                prompt = "[{}. {}]".format(i + 1, formatted_option)
                dispatcher.utter_message(prompt.replace("_", " "))

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

        
class SaveChoiceMovie(Action):

    def name(self):
        return "SaveChoiceMovie"

    def run(self, dispatcher, tracker, domain):        
        from rasa_core.events import UserUtteranceReverted, SlotSet
        matches = tracker.get_slot("matches")
        if matches is None:
            dispatcher.utter_message("Sorry, I didn't catch that")
            return [UserUtteranceReverted()]

        feats = ['movie::title', 'movie::actor', 'movie::rating', 'movie::genre', 'movie::director']

        from database import Database
        choice = matches[0]
        db = Database.get_instance()

        joined_choice = db.remove_fkeys_from_result_set(choice)
        formatted_choice = ", ".join(["{}: {}".format(db.slot_to_column(k),
                            v) for k, v in joined_choice.items() if k in feats])

        dispatcher.utter_message("Ok! You have selected the following"
                                 " movie: [{}]".format(formatted_choice)                       
                                 .replace("_", " "))
        events = []
        for slot, value in choice.items(): 
            events.append(SlotSet(slot, value))
        
        return events + [SlotSet("matches", None)]

        
class TransferMoviePreferencesToScreening(Action):

    def name(self):
        return "TransferMoviePreferencesToScreening"

    def run(self, dispatcher, tracker, domain):        
        from rasa_core.events import SlotSet
        from database import Database
        db = Database.get_instance() 
        events = []

        table_name = "movie"
        table = db.get_table_wname(table_name)
        pkey = db.column_to_slot(table['pkey'], table_name)

        fkey = None
        for column in db.get_table_wname("screening")['columns']:
            if column.get('refs', {}).get('table', "") == table_name:
                if column['refs']['column'] == table['pkey']:
                    fkey = db.column_to_slot(column['column_name'],
                                                   "screening")
        if not fkey:
            dispatcher.utter_message("Sorry, I didn't catch that")
            return []

        preferences = db.select_nth(table_name, {}, 1)
        preferences = dict.fromkeys(preferences, None)

        slots = ['movie::id', 'movie::title', 'movie::genre', 'movie::director', 'movie::plot', 'movie::actor', 'movie::rating', 'movie::cast']
        events.append(SlotSet(fkey, tracker.get_slot(pkey)))
        events.extend([SlotSet(s, None) for s in slots])
        return events 

        
class ProposeTheater(Action):

    def name(self):
        return "ProposeTheater"

    def run(self, dispatcher, tracker, domain):        
        slots = ['ticket_purchase::id', 'ticket_purchase::number_of_kids', 'ticket_purchase::number_of_tickets', 'ticket_purchase::customer_name', 'ticket_purchase::fk_screening', 'screening::id', 'screening::time', 'screening::date', 'screening::price', 'screening::room', 'screening::fk_movie', 'screening::fk_theater', 'movie::id', 'movie::title', 'movie::genre', 'movie::director', 'movie::plot', 'movie::actor', 'movie::rating', 'movie::cast', 'theater::id', 'theater::name', 'theater::chain', 'theater::city', 'theater::address']
        feats = ['theater::name', 'theater::city', 'theater::chain']

        from database import Database, is_value, ordinal_index_to_int
        db = Database.get_instance() 
        matches = tracker.get_slot("matches")

        if matches is None:
            matches = matches if matches else db.kb_lookup("theater",
                                {s : tracker.get_slot(s) for s in slots})
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
            if user_choice and ordinal_index_to_int(user_choice):
                rows = [rows[ordinal_index_to_int(user_choice) - 1]]
                events.append(SlotSet("results_offsets", [0]))
             
            if len(rows) == 1:
                message = "Is this theater what you were" +                                        \
                                               " looking for?"
            else:
                user_config = {s : tracker.get_slot(s) for s in slots}
                user_config = {db.slot_to_column(k) : v for k, v in db                                 \
                                .remove_fkeys_from_result_set(user_config)
                                .items() if is_value(v)}

                message = "There are more than one theater with "   +                              \
                          "{}. Here, let me show you:".format((" and " +                              \
                          "").join(["{} {}".format(k, v) for k, v in                                \
                          user_config.items()]))
            
            dispatcher.utter_message(message.replace("_", " "))
            for i, row in enumerate(rows):
                row = db.remove_fkeys_from_result_set(row)
                formatted_option = ", ".join(["{}: {}".format(db.slot_to_column(k),
                                    v) for k, v in row.items() if k in feats])

                prompt = "[{}. {}]".format(i + 1, formatted_option)
                dispatcher.utter_message(prompt.replace("_", " "))

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

        
class SaveChoiceTheater(Action):

    def name(self):
        return "SaveChoiceTheater"

    def run(self, dispatcher, tracker, domain):        
        from rasa_core.events import UserUtteranceReverted, SlotSet
        matches = tracker.get_slot("matches")
        if matches is None:
            dispatcher.utter_message("Sorry, I didn't catch that")
            return [UserUtteranceReverted()]

        feats = ['theater::name', 'theater::city', 'theater::chain']

        from database import Database
        choice = matches[0]
        db = Database.get_instance()

        joined_choice = db.remove_fkeys_from_result_set(choice)
        formatted_choice = ", ".join(["{}: {}".format(db.slot_to_column(k),
                            v) for k, v in joined_choice.items() if k in feats])

        dispatcher.utter_message("Ok! You have selected the following"
                                 " theater: [{}]".format(formatted_choice)                       
                                 .replace("_", " "))
        events = []
        for slot, value in choice.items(): 
            events.append(SlotSet(slot, value))
        
        return events + [SlotSet("matches", None)]

        
class TransferTheaterPreferencesToScreening(Action):

    def name(self):
        return "TransferTheaterPreferencesToScreening"

    def run(self, dispatcher, tracker, domain):        
        from rasa_core.events import SlotSet
        from database import Database
        db = Database.get_instance() 
        events = []

        table_name = "theater"
        table = db.get_table_wname(table_name)
        pkey = db.column_to_slot(table['pkey'], table_name)

        fkey = None
        for column in db.get_table_wname("screening")['columns']:
            if column.get('refs', {}).get('table', "") == table_name:
                if column['refs']['column'] == table['pkey']:
                    fkey = db.column_to_slot(column['column_name'],
                                                   "screening")
        if not fkey:
            dispatcher.utter_message("Sorry, I didn't catch that")
            return []

        preferences = db.select_nth(table_name, {}, 1)
        preferences = dict.fromkeys(preferences, None)

        slots = ['theater::id', 'theater::name', 'theater::chain', 'theater::city', 'theater::address']
        events.append(SlotSet(fkey, tracker.get_slot(pkey)))
        events.extend([SlotSet(s, None) for s in slots])
        return events 

        
class ResetDependenciesScreening(Action):

    def name(self):
        return "ResetDependenciesScreening"

    def run(self, dispatcher, tracker, domain):        
        dependencies = {'screening::date': [], 'screening::fk_theater': [], 'screening::time': [], 'screening::fk_movie': []}
        from rasa_core.utils.state_history import StateHistory
        updated = StateHistory().get_updated_slots(tracker)

        from database import DONT_CARE
        ignore   = [k for k in updated.keys() if updated[k] == DONT_CARE]
        to_check = [k for k in updated.keys() if k not in ignore]

        from rasa_core.events import SlotSet

        resets = []
        for k in to_check:
            for dep in dependencies.get(k, []):
                if dep not in updated.keys():
                    resets.append(SlotSet(dep, None))
        
        return resets
        
        
class LookupScreening(Action):

    def name(self):
        return "LookupScreening"

    def run(self, dispatcher, tracker, domain):        
        from database import Database, is_value
        slots = ['ticket_purchase::id', 'ticket_purchase::number_of_kids', 'ticket_purchase::number_of_tickets', 'ticket_purchase::customer_name', 'ticket_purchase::fk_screening', 'screening::id', 'screening::time', 'screening::date', 'screening::price', 'screening::room', 'screening::fk_movie', 'screening::fk_theater', 'movie::id', 'movie::title', 'movie::genre', 'movie::director', 'movie::plot', 'movie::actor', 'movie::rating', 'movie::cast', 'theater::id', 'theater::name', 'theater::chain', 'theater::city', 'theater::address']
        db = Database.get_instance() 
        matches = db.kb_lookup("screening", {s : tracker.get_slot(s)                                \
                                                       for s in slots})
        from rasa_core.utils.state_history import StateHistory
        from rasa_core.events import SlotSet
        if not matches:
            last_set_slots = StateHistory().get_events(tracker, 
                             event_type='user')[-1]['parse_data']['entities']
            
            configuration = db.remove_fkeys_from_result_set({s :                                       \
                            tracker.get_slot(s) for s in slots if                                       \
                            is_value(tracker.get_slot(s))})
            configuration = " and ".join(["{} {}".format(db.slot_to_column(k), v)                   \
                             for k, v in configuration.items()])
            
            dispatcher.utter_message("Unfortunately, I couldn't find any"
                                     " screening with {}".format(configuration)                    \
                                     .replace("_", " "))

            return [SlotSet(e['entity'], None) for e in last_set_slots]
            
        import random
        prompts = ["Alright, got that", "Understood", "Mm-mmh"]
        dispatcher.utter_message(random.choice(prompts).replace("_", " "))

        return [SlotSet("matches", matches), SlotSet("results_offsets", [0])]

        
class RelaxLastRequest(Action):

    def name(self):
        return "RelaxLastRequest"

    def run(self, dispatcher, tracker, domain):        
        from rasa_core.utils.state_history import StateHistory
        last_request = StateHistory().get_latest_action(tracker)

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

        
class ProposeScreening(Action):

    def name(self):
        return "ProposeScreening"

    def run(self, dispatcher, tracker, domain):        
        slots = ['ticket_purchase::id', 'ticket_purchase::number_of_kids', 'ticket_purchase::number_of_tickets', 'ticket_purchase::customer_name', 'ticket_purchase::fk_screening', 'screening::id', 'screening::time', 'screening::date', 'screening::price', 'screening::room', 'screening::fk_movie', 'screening::fk_theater', 'movie::id', 'movie::title', 'movie::genre', 'movie::director', 'movie::plot', 'movie::actor', 'movie::rating', 'movie::cast', 'theater::id', 'theater::name', 'theater::chain', 'theater::city', 'theater::address']
        feats = ['screening::time', 'screening::date']

        from database import Database, is_value, ordinal_index_to_int
        db = Database.get_instance() 
        matches = tracker.get_slot("matches")

        if matches is None:
            matches = matches if matches else db.kb_lookup("screening",
                                {s : tracker.get_slot(s) for s in slots})
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
            if user_choice and ordinal_index_to_int(user_choice):
                rows = [rows[ordinal_index_to_int(user_choice) - 1]]
                events.append(SlotSet("results_offsets", [0]))
             
            if len(rows) == 1:
                message = "Is this screening what you were" +                                        \
                                               " looking for?"
            else:
                user_config = {s : tracker.get_slot(s) for s in slots}
                user_config = {db.slot_to_column(k) : v for k, v in db                                 \
                                .remove_fkeys_from_result_set(user_config)
                                .items() if is_value(v)}

                message = "There are more than one screening with "   +                              \
                          "{}. Here, let me show you:".format((" and " +                              \
                          "").join(["{} {}".format(k, v) for k, v in                                \
                          user_config.items()]))
            
            dispatcher.utter_message(message.replace("_", " "))
            for i, row in enumerate(rows):
                row = db.remove_fkeys_from_result_set(row)
                formatted_option = ", ".join(["{}: {}".format(db.slot_to_column(k),
                                    v) for k, v in row.items() if k in feats])

                prompt = "[{}. {}]".format(i + 1, formatted_option)
                dispatcher.utter_message(prompt.replace("_", " "))

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

        
class SaveChoiceScreening(Action):

    def name(self):
        return "SaveChoiceScreening"

    def run(self, dispatcher, tracker, domain):        
        from rasa_core.events import UserUtteranceReverted, SlotSet
        matches = tracker.get_slot("matches")
        if matches is None:
            dispatcher.utter_message("Sorry, I didn't catch that")
            return [UserUtteranceReverted()]

        feats = ['screening::time', 'screening::date']

        from database import Database
        choice = matches[0]
        db = Database.get_instance()

        joined_choice = db.remove_fkeys_from_result_set(choice)
        formatted_choice = ", ".join(["{}: {}".format(db.slot_to_column(k),
                            v) for k, v in joined_choice.items() if k in feats])

        dispatcher.utter_message("Ok! You have selected the following"
                                 " screening: [{}]".format(formatted_choice)                       
                                 .replace("_", " "))
        events = []
        for slot, value in choice.items(): 
            events.append(SlotSet(slot, value))
        
        return events + [SlotSet("matches", None)]

        
class TransferScreeningPreferencesToTicketPurchase(Action):

    def name(self):
        return "TransferScreeningPreferencesToTicketPurchase"

    def run(self, dispatcher, tracker, domain):        
        from rasa_core.events import SlotSet
        from database import Database
        db = Database.get_instance() 
        events = []

        table_name = "screening"
        table = db.get_table_wname(table_name)
        pkey = db.column_to_slot(table['pkey'], table_name)

        fkey = None
        for column in db.get_table_wname("ticket_purchase")['columns']:
            if column.get('refs', {}).get('table', "") == table_name:
                if column['refs']['column'] == table['pkey']:
                    fkey = db.column_to_slot(column['column_name'],
                                                   "ticket_purchase")
        if not fkey:
            dispatcher.utter_message("Sorry, I didn't catch that")
            return []

        preferences = db.select_nth(table_name, {}, 1)
        preferences = dict.fromkeys(preferences, None)

        slots = ['screening::id', 'screening::time', 'screening::date', 'screening::price', 'screening::room', 'screening::fk_movie', 'screening::fk_theater']
        events.append(SlotSet(fkey, tracker.get_slot(pkey)))
        events.extend([SlotSet(s, None) for s in slots])
        return events 

        
class InsertTicketPurchase(Action):

    def name(self):
        return "InsertTicketPurchase"

    def run(self, dispatcher, tracker, domain):        
        from database import Database, is_value
        db = Database.get_instance() 
        slots = ['ticket_purchase::id', 'ticket_purchase::number_of_kids', 'ticket_purchase::number_of_tickets', 'ticket_purchase::customer_name', 'ticket_purchase::fk_screening']

        user_config = {s : tracker.get_slot(s) for s in slots                                          \
                        if is_value(tracker.get_slot(s))}

        user_config = db.join_result_set_on_fkeys(user_config)
        formatted_config = ", ".join(["{} {}: {}".format(db                                       \
                .slot_to_table(k), db.slot_to_column(k), v) for k, 
                v in user_config.items()])

        dispatcher.utter_message("Ok. As requested by you, I have registered your "
                                 "ticket_purchase for [{}]".format(formatted_config)                     \
                                 .replace("_", " "))

        queries = tracker.get_slot("queries")
        queries.append(db.query_to_dict("insert", "ticket_purchase", 
                      {s : tracker.get_slot(s) for s in slots}))
        
        from rasa_core.events import SlotSet
        return [SlotSet("queries", queries)]

        
class CompleteInsertTicketPurchaseTask(Action):

    def name(self):
        return "CompleteInsertTicketPurchaseTask"

    def run(self, dispatcher, tracker, domain):        
        dispatcher.utter_message("Now, is there anything else I can "
                                 "help you with or should I finalize?")
        # change this to manipulate dialog state reset at task completion
        from rasa_core.events import AllSlotsReset, SlotSet
        return [SlotSet("results_displayed", tracker.get_slot("results_displayed")),
                AllSlotsReset, SlotSet("queries", tracker.get_slot("queries")),
                SlotSet("results_offsets", [0])]

        
class Finalize(Action):

    def name(self):
        return "Finalize"

    def run(self, dispatcher, tracker, domain):        
        # uncomment this if you want queries that modify the database to be run
        #from database import Database
        #Database.get_instance().queries_from_dict(tracker.get_slot("queries"))
        from rasa_core.events import SlotSet
        return [SlotSet("queries", [])]

        
class ReloadMovieOptions(Action):

    def name(self):
        return "ReloadMovieOptions"

    def run(self, dispatcher, tracker, domain):        
        from rasa_core.events import SlotSet
        return [SlotSet(k, None) for k in ['movie::id', 'movie::plot', 'movie::cast']]

        
class ReloadTheaterOptions(Action):

    def name(self):
        return "ReloadTheaterOptions"

    def run(self, dispatcher, tracker, domain):        
        from rasa_core.events import SlotSet
        return [SlotSet(k, None) for k in ['theater::id', 'theater::address']]

        
class RestoreScreeningPreferencesFromTicketPurchase(Action):

    def name(self):
        return "RestoreScreeningPreferencesFromTicketPurchase"

    def run(self, dispatcher, tracker, domain):        
        from rasa_core.events import SlotSet
        from database import Database
        db = Database.get_instance()
        events = []

        table_name = "screening"
        table = db.get_table_wname(table_name)
        pkey = db.column_to_slot(table['pkey'], table_name)

        fkey = None
        for column in db.get_table_wname("ticket_purchase")['columns']:
            if column.get('refs', {}).get('table', "") == table_name:
                if column['refs']['column'] == table['pkey']:
                    fkey = db.column_to_slot(column['column_name'],                                     \
                                                   "ticket_purchase")
        if not fkey:
            dispatcher.utter_message("Sorry, I didn't catch that")
            return []

        events.append(SlotSet(fkey, None))
        preferences = db.select_nth(table_name, 
          {pkey : tracker.get_slot(fkey)}, 1)

        dependencies = {'screening::date': [], 'screening::fk_theater': [], 'screening::time': [], 'screening::fk_movie': []}
        from rasa_core.utils.state_history import StateHistory
        updated = StateHistory().get_updated_slots(tracker)
        for slot in updated:
            deps = dependencies.get(slot, [])
            for dep in deps:
                events.append(SlotSet(dep, None))

        for slot, value in preferences.items():
            events.append(SlotSet(slot, value))

        return events

        
class RestoreMoviePreferencesFromScreening(Action):

    def name(self):
        return "RestoreMoviePreferencesFromScreening"

    def run(self, dispatcher, tracker, domain):        
        from rasa_core.events import SlotSet
        from database import Database
        db = Database.get_instance()
        events = []

        table_name = "movie"
        table = db.get_table_wname(table_name)
        pkey = db.column_to_slot(table['pkey'], table_name)

        fkey = None
        for column in db.get_table_wname("screening")['columns']:
            if column.get('refs', {}).get('table', "") == table_name:
                if column['refs']['column'] == table['pkey']:
                    fkey = db.column_to_slot(column['column_name'],                                     \
                                                   "screening")
        if not fkey:
            dispatcher.utter_message("Sorry, I didn't catch that")
            return []

        events.append(SlotSet(fkey, None))
        preferences = db.select_nth(table_name, 
          {pkey : tracker.get_slot(fkey)}, 1)

        dependencies = {'movie::director': ['movie::actor', 'movie::rating', 'movie::genre', 'movie::title'], 'movie::title': ['movie::actor', 'movie::director', 'movie::genre', 'movie::rating'], 'movie::genre': ['movie::actor', 'movie::director', 'movie::title'], 'movie::actor': ['movie::rating', 'movie::genre', 'movie::title', 'movie::director'], 'movie::rating': ['movie::actor', 'movie::director', 'movie::title']}
        from rasa_core.utils.state_history import StateHistory
        updated = StateHistory().get_updated_slots(tracker)
        for slot in updated:
            deps = dependencies.get(slot, [])
            for dep in deps:
                events.append(SlotSet(dep, None))

        for slot, value in preferences.items():
            events.append(SlotSet(slot, value))

        return events

        
class RepeatLastTurn(Action):

    def name(self):
        return "RepeatLastTurn"

    def run(self, dispatcher, tracker, domain):        
        from rasa_core.utils.state_history import StateHistory
        last_turn = StateHistory().get_utterances(tracker, speaker="bot")[-1]
        if last_turn:
            dispatcher.utter_message("I said: {}".format("; ".join(last_turn)))
        else:
            dispatcher.utter_message("I haven't said anything yet")

        return []

class LoadPrevOptions(Action):

    def name(self):
        return "LoadPrevOptions"

    def run(self, dispatcher, tracker, domain):        
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

        
class ReloadScreeningOptions(Action):

    def name(self):
        return "ReloadScreeningOptions"

    def run(self, dispatcher, tracker, domain):        
        from rasa_core.events import SlotSet
        return [SlotSet(k, None) for k in ['screening::id', 'screening::price', 'screening::room']]

        
class LoadHeadOptions(Action):

    def name(self):
        return "LoadHeadOptions"

    def run(self, dispatcher, tracker, domain):        
        from rasa_core.events import SlotSet
        cur_offsets = tracker.get_slot("results_offsets")

        if cur_offsets[-1] != 0:
            cur_offsets.append(0)
            dispatcher.utter_message("Ok, I'll show you the first {} results"
                                     "".format(tracker.get_slot("results_displayed")))

            return [SlotSet("results_offsets", cur_offsets)]

        dispatcher.utter_message("You are already looking at the first results")
        return []

        
class LoadMoreOptions(Action):

    def name(self):
        return "LoadMoreOptions"

    def run(self, dispatcher, tracker, domain):        
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

        
