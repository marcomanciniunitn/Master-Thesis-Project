from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from rasa_core.actions.action import ACTION_LISTEN_NAME


class StateHistory:
    """
    Set of functions to retrieve information from tracker.current_state:
    TODO: Move tracker to __init__ ???

    """

    def get_events(self, tracker, event_type=None):
        """
        get event by type
        :param tracker:
        :param event_type:
        :return:
        """
        state = tracker.current_state(True)
        if event_type:
            events = [e for e in state['events'] if e['event'] == event_type]
        else:
            events = state['events']
        return events

    def get_latest_intent(self, tracker):
        """
        get latest user intent

        :param tracker:
        :return:
        """
        return tracker.latest_message.intent["name"]

    def get_latest_intent_confidence(self, tracker):
        """
        :param tracker:
        :return:
        """
        return tracker.latest_message.intent.get('confidence', 0.0)

    def get_latest_action(self, tracker):
        """
        get latest system action

        :param tracker:
        :return:
        """
        return tracker.latest_action_name

    def get_intent_history(self, tracker):
        """
        get user intent history

        :param tracker:
        :return:
        """
        state = tracker.current_state(True)
        intents = [e['parse_data']['intent']['name'] for e in state['events']
                   if e['event'] == 'user']
        return intents

    def get_action_history(self, tracker):
        """
        get system action history

        :param tracker:
        :return:
        """
        state   = tracker.current_state(True)
        actions = [e['name'] for e in state['events']
                   if e['event'] == 'action' and e['name'] != ACTION_LISTEN_NAME]
        return actions

    def get_previous_intent(self, tracker):
        """
        get previous user intent

        :param tracker:
        :return:
        """
        intents = self.get_intent_history(tracker)
        return intents[-2] if len(intents) > 1 else None

    def get_previous_action(self, tracker):
        """
        get previous system action
        INFO: similar to tracker.latest_action_name, but without action_listen

        :param tracker:
        :return:
        """
        actions = self.get_action_history(tracker)
        return actions[-1] if len(actions) > 0 else None

    # Slot Related Functions
    def get_slot_history(self, tracker):
        """
        extract slot history from the tracker ('event': 'slot')
        :param tracker:
        :return:
        """
        return self.get_events(tracker, 'slot')

    def get_latest_set_slots(self, tracker):
        """
        Get slots set by the last user message

        :param tracker:
        :return:
        """
        slot_history = self.get_slot_history(tracker)
        latest_time  = self.get_latest_intent_time(tracker)
        slot_events  = {e['name']: e['value'] for e in slot_history
                        if e['timestamp'] >= latest_time}
        return slot_events

    def get_updated_slots(self, tracker):
        """
        Get slots updated by latest user message
        :param tracker:
        :return:
        """
        # get slots set by the latest user message
        latest_set_slots  = self.get_latest_set_slots(tracker)
        # get all slot events from history
        slot_history      = self.get_slot_history(tracker)
        # remove latest slot events from history
        prev_slot_history = slot_history[0:-len(latest_set_slots)]

        # recreate the state slot values
        slot_events  = {e['name']: e['value'] for e in prev_slot_history}
        slot_updates = {k: v for k, v in slot_events.items() if
                        k in latest_set_slots.keys() and v != latest_set_slots[k]}
        return slot_updates

    # Utterance Related Function
    def get_utterances(self, tracker, speaker=None):
        """
        get user or system utterances
        since system can have several action in a turn, use block
        :param tracker:
        :param speaker:
        :return:
        """
        events = self.get_events(tracker)
        speakers = ['user', 'bot']
        turns = []
        block = []
        for e in events:
            if e['event'] == speaker and e['text']:
                block.append(e['text'])
            elif e['event'] in speakers and e['event'] != speaker:
                turns.append(block)
                block = []
        if block:
            turns.append(block)

        return turns

    def get_latest_user_utterance(self, tracker):
        """
        :param tracker:
        :return:
        """
        turns = self.get_utterances(tracker, 'user')
        text  = ' . '.join(turns[-1]) if len(turns) > 1 else None
        return text

    def get_previous_user_utterance(self, tracker):
        """
        :param tracker:
        :return:
        """
        turns = self.get_utterances(tracker, 'user')
        text  = ' . '.join(turns[-2]) if len(turns) > 1 else None
        return text

    def get_latest_system_utterance(self, tracker):
        """
        :param tracker:
        :return:
        """
        turns = self.get_utterances(tracker, 'bot')
        text = ' . '.join(turns[-1]) if len(turns) > 0 else None
        return text

    def get_previous_system_utterance(self, tracker):
        """
        :param tracker:
        :return:
        """
        turns = self.get_utterances(tracker, 'bot')
        text = ' . '.join(turns[-2]) if len(turns) > 1 else None
        return text

    # Time Related Functions
    def get_event_timestamps(self, tracker, event_type=None):
        """
        Extract event timestamps

        :param tracker:
        :return:
        """
        events = self.get_events(tracker, event_type)
        times  = [e['timestamp'] for e in events]
        return times

    def get_latest_intent_time(self, tracker):
        times = self.get_event_timestamps(tracker, 'user')
        return times[-1] if len(times) > 0 else 0.0

    def get_previous_intent_time(self, tracker):
        times = self.get_event_timestamps(tracker, 'user')
        return times[-2] if len(times) > 1 else 0.0

    def get_slot_time(self, tracker, slot_name):
        """
        get the time of the last update of the slot

        :param tracker:
        :param slot: slot name
        :return:
        """
        slot_events = self.get_slot_history(tracker)
        time = 0.0
        for s in slot_events:
            if s['name'] == slot_name:
                # will output the latest update time
                # {"event": "slot", "timestamp": 0.00, "name": "slot_name", "value": "slot_value"}
                time = s['timestamp']
        return time

    def get_grouped_action_history(self, tracker):
        """

        :param actions:
        :param index:
        :return:
        """
        state = tracker.current_state(True)
        actions = [e['name'] for e in state['events']
                   if e['event'] == 'action' and e['name'] != ACTION_LISTEN_NAME]

        grouped_actions = []
        temp_list = []
        last_action_listen_index = 0
        last_action_index = 0
        for i, event in enumerate(state['events']):
            if event['event'] == 'action':
                if event['name'] != ACTION_LISTEN_NAME:
                    temp_list.append(event['name'])
                else:
                    grouped_actions.append(temp_list)
                    temp_list = []
                    last_action_listen_index = i

                last_action_index = i
        # check if we are at the beginning of the turn, if so add an empty list
        # logger.debug("Last Action Listen Index: {} vs Last Action Index : {}".format(last_action_listen_index,last_action_index))
        if len(temp_list) > 0 or last_action_listen_index == last_action_index:
            grouped_actions.append(temp_list)

        # logger.debug("Actions found: {} vs grouped actions: {}".format(actions, grouped_actions))

        return grouped_actions