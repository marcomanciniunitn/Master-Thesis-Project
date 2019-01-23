from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import argparse
import logging
import uuid
from difflib import SequenceMatcher

try:
    import matplotlib.pyplot as plt
except Exception:
    print("Not found module")
from tqdm import tqdm
from typing import Text, List, Tuple
import time
import rasa_core
from rasa_core import utils
from rasa_core.agent import Agent, ExtendedAgent
from rasa_core.events import ActionExecuted, UserUttered, UserDirective
from rasa_core.interpreter import RegexInterpreter, RasaNLUInterpreter
from rasa_core import training
from rasa_core.training import TrainingsDataGenerator
from rasa_nlu.evaluate import plot_confusion_matrix, log_evaluation_table
import editdistance

logger = logging.getLogger(__name__)


def create_argument_parser():
    """Create argument parser for the evaluate script."""

    parser = argparse.ArgumentParser(
            description='evaluates a dialogue model')
    parser.add_argument(
            '-s', '--stories',
            type=str,
            required=True,
            help="file or folder containing stories to evaluate on")
    parser.add_argument(
            '-m', '--max_stories',
            type=int,
            default=None,
            help="maximum number of stories to test on")
    parser.add_argument(
            '-d', '--core',
            required=True,
            type=str,
            help="core model to run with the server")
    parser.add_argument(
            '-u', '--nlu',
            type=str,
            help="nlu model to run with the server. None for regex interpreter")
    parser.add_argument(
            '-p', '--message-preprocessor',
            type=str,
            help="The message pre-processor parameter, if None => no message pre-processor provided")
    parser.add_argument(
            '-i', '--interpreter-class',
            type=str,
            help="The interpreter class parameter, if None => RASANluInterpreter provided")
    parser.add_argument(
            '-o', '--output',
            type=str,
            default="story_confmat.pdf",
            help="output path for the created evaluation plot")

    utils.add_logging_option_arguments(parser)
    return parser


def align_lists(pred, actual):
    # type: (List[Text], List[Text]) -> Tuple[List[Text], List[Text]]
    """Align two lists trying to keep same elements at the same index.

    If lists contain different items at some indices, the algorithm will
    try to find the best alignment and pad with `None`
    values where necessary."""

    padded_pred = []
    padded_actual = []
    s = SequenceMatcher(None, pred, actual)

    for tag, i1, i2, j1, j2 in s.get_opcodes():
        padded_pred.extend(pred[i1:i2])
        padded_pred.extend(["None"] * ((j2 - j1) - (i2 - i1)))

        padded_actual.extend(actual[j1:j2])
        padded_actual.extend(["None"] * ((i2 - i1) - (j2 - j1)))

    return padded_pred, padded_actual


def actions_since_last_utterance(tracker):
    # type: (rasa_core.trackers.DialogueStateTracker) -> List[Text]
    """Extract all events after the most recent utterance from the user."""

    actions = []
    for e in reversed(tracker.events):
        if isinstance(e, UserUttered) or isinstance(e, UserDirective):
            break
        elif isinstance(e, ActionExecuted):
            actions.append(e.action_name)
    actions.reverse()
    return actions


def compute_dialogue_success_rate(dialogue_predictions, dialogue_real):
    success_counter = 0
    for preds, reals in zip(dialogue_predictions, dialogue_real):
        if preds == reals:
            success_counter +=1
    dialogue_success_rate = float(success_counter)/float(len(dialogue_predictions))
    print("Dialogue Success Rate: {} % on {} dialogues".format(
        float(success_counter)*100/float(len(dialogue_predictions)),
        len(dialogue_predictions)))
    return dialogue_success_rate


def simulate_dialogue_execution_and_compare(agent, tracker, dialogue_id, message_preprocessor,
                                            turn_level_preds, turn_level_actual, dialogue_predictions, dialogue_actual,
                                            preds, actual):
    sender_id = "automatic.test-test-default-" + str(time.time()) + "-" + uuid.uuid4().hex
    # logger.debug("Tracker number is {} and The current sender_id is {}".format(j, sender_id))
    if dialogue_id <= len(dialogue_actual) and dialogue_id <= len(dialogue_predictions):
        dialogue_actual.append([])
        dialogue_predictions.append([])

    events = list(tracker.events)
    actions_between_utterances = []
    last_prediction = []
    first_time = True
    for i, event in enumerate(events[1:]):
        # logger.debug("Event number: {} = {}".format(i,event))
        if isinstance(event, UserUttered) or isinstance(event, UserDirective):
            p, a = align_lists(last_prediction, actions_between_utterances)
            # store predictions at turn level
            turn_level_preds.append(last_prediction)
            turn_level_actual.append(actions_between_utterances)
            # store predictions at dialogue level
            dialogue_predictions[dialogue_id].append(last_prediction)
            dialogue_actual[dialogue_id].append(actions_between_utterances)
            # store predictions as list
            preds.extend(p)
            actual.extend(a)
            if first_time:
                logger.warning("Time when agent started handling messages : {}".format(time.time()))
                first_time =False
            actions_between_utterances = []
            #if isinstance(event, UserDirective):
            #    training.ExtendedStoryFileReader.set_testing_to_true(event.parse_data)
            #    agent.handle_message(event.parse_data, sender_id=sender_id, message_preprocessor=message_preprocessor)
            #else:
            agent.handle_message(event.text, sender_id=sender_id, message_preprocessor=message_preprocessor)

            # TAKE THIS INTO ACCOUNT
            tracker = agent.tracker_store.retrieve(sender_id)
            last_prediction = actions_since_last_utterance(tracker)
            # logger.debug("At event {} actions are {}".format(i,last_prediction))
        elif isinstance(event, ActionExecuted):
            actions_between_utterances.append(event.action_name)

    if last_prediction:
        turn_level_preds.append(last_prediction)
        turn_level_actual.append(actions_between_utterances)

        preds.extend(last_prediction)
        preds_padding = len(actions_between_utterances) - \
                        len(last_prediction)
        preds.extend(["None"] * preds_padding)

        actual.extend(actions_between_utterances)
        actual_padding = len(last_prediction) - \
                         len(actions_between_utterances)
        actual.extend(["None"] * actual_padding)



def collect_story_predictions(resource_name, policy_model_path, nlu_model_path,
                              max_stories=None, shuffle_stories=True, message_preprocessor=None,
                              interpreter_class=None):
    """Test the stories from a file, running them through the stored model."""

    if nlu_model_path is not None and interpreter_class is None:
        interpreter = RasaNLUInterpreter(model_directory=nlu_model_path)
    elif nlu_model_path is None:
        interpreter = RegexInterpreter()
    else:
        interpreter = interpreter_class(nlu_model_path)

    interpreter = RegexInterpreter()

    agent = Agent.load(policy_model_path, interpreter=interpreter)
    story_graph = training.extract_story_graph_evaluate(resource_name, agent.domain, interpreter)

    max_history = agent.policy_ensemble.policies[0].max_history

    g = TrainingsDataGenerator(story_graph, agent.domain,
                               agent.featurizer,
                               max_history=max_history,
                               use_story_concatenation=False,
                               tracker_limit=1500,
                               remove_duplicates=False,
                               augmentation_factor=0)
    data = g.generate()

    completed_trackers = data.metadata["trackers"]
    logger.info(
            "Evaluating {} stories\nProgress:".format(len(completed_trackers)))
    turn_level_preds = []
    turn_level_actual = []
    dialogue_predictions = []
    dialogue_actual = []
    preds = []
    actual = []

    for j, tracker in enumerate(tqdm(completed_trackers)):
        simulate_dialogue_execution_and_compare(agent, tracker, j, message_preprocessor,
                                                turn_level_preds, turn_level_actual,
                                                dialogue_predictions, dialogue_actual, preds, actual)

    if logger.getEffectiveLevel() == 10: # logger is in debug mode
        logger.debug("Number of actual turns in the dialogue : {}".format(len(turn_level_actual)))
        logger.debug(" ---------------- actuals ----------------")
        for i,turn in enumerate(turn_level_actual):
            logger.debug("Turn {} -> {}".format(i, turn))
        logger.debug("Number of predicted turns in the dialogue : {}".format(len(turn_level_preds)))
        logger.debug(" ---------------- predicted ----------------")
        for i,turn in enumerate(turn_level_preds):
            logger.debug("Turn {} -> {}".format(i, turn))

        turn_index = 0
        for turn_predictions, turn_actuals in zip(turn_level_preds, turn_level_actual):
            if turn_predictions != turn_actuals:
                logger.debug("At turn {} : predicted_actions = {} and real_actions = {}".format(turn_index,
                                                                                                turn_predictions,
                                                                                                turn_actuals))
            turn_index +=1

    # Compute dialogue success rate
    compute_dialogue_success_rate(dialogue_predictions, dialogue_actual)


    return actual, preds


def compute_and_print_action_error_rate(references, preds):
    edit_distance = editdistance.eval(references, preds)
    action_error_rate = edit_distance/len(references)

    print("The action error rate is : {}".format(action_error_rate))


def run_story_evaluation(resource_name, policy_model_path, nlu_model_path,
                         out_file, max_stories, message_preprocessor=None, interpreter_class=None):
    """Run the evaluation of the stories, plots the results."""
    from sklearn.metrics import confusion_matrix
    from sklearn.utils.multiclass import unique_labels

    test_y, preds = collect_story_predictions(resource_name, policy_model_path,
                                              nlu_model_path, max_stories,
                                              message_preprocessor = message_preprocessor,
                                              interpreter_class = interpreter_class
                                              )

    log_evaluation_table(test_y, preds)
    cnf_matrix = confusion_matrix(test_y, preds)
    plot_confusion_matrix(cnf_matrix, classes=unique_labels(test_y, preds),
                          title='Action Confusion matrix')
    compute_and_print_action_error_rate(test_y,preds)
    fig = plt.gcf()
    fig.set_size_inches(int(20), int(20))
    fig.savefig(out_file, bbox_inches='tight')


def instance_message_preprocessor_class(class_path):
    preproc_class = ExtendedAgent.found_class_object(class_path)
    if preproc_class is None:
        return None
    logger.debug("Class object: {}".format(preproc_class))

    return preproc_class()


if __name__ == '__main__':
    # Running as standalone python application
    arg_parser = create_argument_parser()
    cmdline_args = arg_parser.parse_args()

    #interpreter_class = ExtendedAgent.found_class_object(cmdline_args.interpreter_class)
    #logger.debug("The interpreter class found is : {}".format(interpreter_class))


    logging.basicConfig(level=cmdline_args.loglevel)
    run_story_evaluation(cmdline_args.stories,
                         cmdline_args.core,
                         cmdline_args.nlu,
                         cmdline_args.output,
                         cmdline_args.max_stories,
                         message_preprocessor=None,
                         interpreter_class=None)
    logger.info("Finished evaluation")
