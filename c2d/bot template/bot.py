from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import argparse
import logging
import warnings
import random
import string

from rasa_core import utils
from rasa_core.agent import Agent, ExtendedAgent, CookieCutterAgent
from rasa_core.policies.memoization import MemoizationPolicy
from rasa_core.policies.keras_policy import KerasPolicy, CookieCutterKerasPolicy
from rasa_core.policies.ensemble import CookieCutterSimplePolicyEnsemble
from rasa_core.channels.console import ConsoleInputChannel, ExtendedConsoleInputChannel
from rasa_core.interpreter import RasaNLUInterpreter
from rasa_core.tracker_store import RedisTrackerStore, InMemoryTrackerStore
from rasa_core.preprocessors import MessagePreprocessor
from rasa_core.channels.exposable_http_channel import HttpInputChannel
from rasa_core.channels.vui import VUIInput

from rasa_core.text_featurizers import BagOfWords, EmbeddingCache


import json
from pathlib import Path
import os
logger = logging.getLogger(__name__)

def generate_random_string(N):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=N))

def choose_featurization(model_path, featurization="ents"):
    if featurization not in ["ents", "bow", "usem", "elmo"]:
        print("[!] DM train featurization can be: 'ents', 'bow', "
              "'usem' or 'elmo'. Please provide one of them!")
        quit()
    
    if featurization == "ents":
        model_path = model_path + "_entities"
    elif featurization == "bow":
        model_path = model_path + "_bow"
        bow = BagOfWords.get_instance(sentence_file="data/sentences.txt")
        bow.dump_instance(instance_file="models/bow.pck")
    elif featurization == "usem":
        model_path = model_path + "_usem"
        EmbeddingCache.get_instance(module="usem", cache_file="data/embeddings.pickle")
    elif featurization == "elmo":
        model_path = model_path + "_elmo"
        EmbeddingCache.get_instance(module="elmo", cache_file="data/embeddings.pickle")

    return model_path

def fine_tune(agent_folder="models/dialogue", training_data_file="data/fine_tune_story.md",
              validation_data_file="data/validation.md", featurization="ents"):

    from rasa_core.dispatcher import JinjaDispatcher
    from rasa_core.domain import JinjaDomain
    import os

    agent_folder = choose_featurization(agent_folder, featurization)

    """

    :param path_to_scenario_file:
    :param nlu_folder: the relative path starting from the current file folder to the nlu model directory
    :param agent_folder: the relative path starting from the current file folder to the dialogue model directory
    :param online: the flag that tells if the script is connected online or not
    :param standalone: of the app runs standalone or we want to create only the wsgi app
    :return:
    """
    main_folder_path = os.path.dirname(os.sys.argv[0])
    domain_folder = os.path.join(main_folder_path, agent_folder)

    print("Loading Agent")
    domain_file = os.path.join(domain_folder,'domain.yml')
    #domain_object = JinjaDomain.load(domain_file)
    #redis_tracker = create_tracker_store(domain_object)
    inMemo_tracker = InMemoryTrackerStore(domain_file)
    message_preprocessor = MessagePreprocessor(w2n=True)

    print("The current domain file is {}".format(domain_file))



def load_agent(nlu_folder="models/nlu/default/current", agent_folder="models/dialogue",
               path_to_scenario_file="wismo/v1/data/test/dialogue", online=True,
               standalone=True, vui=True,  nlu_config_file='ensemble.json', 
               nlu_off=False, preprocessor_off=False, featurization="ents", 
               feedback=False, server_bot_folder="/var/www/feedback/"):

    from rasa_core.dispatcher import JinjaDispatcher
    from rasa_core.domain import JinjaDomain
    import os

    agent_folder = choose_featurization(agent_folder, featurization)
    """

    :param path_to_scenario_file:
    :param nlu_folder: the relative path starting from the current file folder to the nlu model directory
    :param agent_folder: the relative path starting from the current file folder to the dialogue model directory
    :param online: the flag that tells if the script is connected online or not
    :param standalone: of the app runs standalone or we want to create only the wsgi app
    :return:
    """

    main_folder_path = os.path.dirname(os.sys.argv[0])
    domain_folder = os.path.join(main_folder_path, agent_folder)


    if nlu_off:
        interpreter = RegexInterpreter()
    else:
        if online and not vui:
            interpreter = RasaNLUInterpreter("models/nlu/default/")
            #interpreter = JsonInterpreter()
        else:
            try:
                # interpreter = EnsembleInterpreter(os.path.join(main_folder_path, agent_folder))
                nlu_path = os.path.join(main_folder_path, nlu_folder)
                #interpreter = EnsembleInterpreter( os.path.join(nlu_path, nlu_config_file))
                interpreter = RasaNLUInterpreter("models/nlu/default/current")  
            except FileNotFoundError:
                # if it fails, try real path
                main_folder_path = os.path.dirname(os.path.realpath(__file__))
                domain_folder = os.path.join(main_folder_path, agent_folder)
                nlu_path = os.path.join(main_folder_path, nlu_folder)
                interpreter = EnsembleInterpreter(os.path.join(nlu_path, nlu_config_file))
    
    print("Loading Agent")
    domain_file = os.path.join(domain_folder,'domain.yml')
    #domain_object = JinjaDomain.load(domain_file)
    #redis_tracker = create_tracker_store(domain_object)
    inMemo_tracker = InMemoryTrackerStore(domain_file)
    message_preprocessor = MessagePreprocessor(w2n=True)

    print("The current domain file is {}".format(domain_file))

    agent = CookieCutterAgent.load(os.path.join(main_folder_path,agent_folder), tracker_store=inMemo_tracker,
                               interpreter=interpreter)
    if not vui:
        http_input_channel = HttpInputChannel(5000, "", False, AlexaInput())
    else:
        http_input_channel = HttpInputChannel(5000, "", False, VUIInput(display_always=True, ssml_enabled=True,
                                                                        action_enabled=True))
    print("Server is running")
    random_sender_id = "TEST.COMMANDLINE." + generate_random_string(32)
    if online:
        http_input_channel.set_standalone(standalone)
        agent.handle_channel(http_input_channel,
                             message_preprocessor=message_preprocessor if not preprocessor_off else None, feedback=feedback, server_bot_folder=server_bot_folder)
    else:
        agent.handle_channel(ExtendedConsoleInputChannel(random_sender_id, resource_path=path_to_scenario_file),
                             message_preprocessor=message_preprocessor if not preprocessor_off else None, feedback=feedback, server_bot_folder=server_bot_folder)

    return agent, http_input_channel


def run(online=True, standalone=True, vui=True, nlu_off=False, 
        preprocessor_off=False, featurization="ents",  
        feedback=False, server_bot_folder="/var/www/feedback/"):
    
    return load_agent(online=online, standalone=standalone, vui=vui, 
        nlu_off=nlu_off, preprocessor_off=preprocessor_off, 
        featurization=featurization, feedback=feedback, 
        server_bot_folder=server_bot_folder)


def compile_and_finetune(nlu_folder="models/nlu/default/current", agent_folder="models/dialogue",
            summary="/home/doomdiskday/Desktop/experiments/error_analysis/summaries/summary.json",
            dump_f="/home/doomdiskday/Desktop/experiments/error_analysis/summaries/full_interaction.json",
            fine_tune_data_file="data/fine_tune_story.md", validation_data_file="data/validation.md",
            featurization="ents"):
    
    import os
    with open(summary) as f:
        dials = json.load(f)

    agent_folder = choose_featurization(agent_folder, featurization)

    main_folder_path = os.path.dirname(os.sys.argv[0])
    domain_folder = os.path.join(main_folder_path, agent_folder)
    interpreter = RasaNLUInterpreter("models/nlu/default/current")
    inMemo_tracker = InMemoryTrackerStore(domain_file)
    message_preprocessor = MessagePreprocessor(w2n=True)


    agent = CookieCutterAgent.load(os.path.join(main_folder_path,agent_folder), 
                               tracker_store=inMemo_tracker, interpreter=None)
    messages = {}
    for d in dials:
        intents = []
        if d['correct'] == False and d['retagged']:
            print(d['id'])
            for step in d['retagged_interaction']:
                if step[0] == "*":
                    intents.append(' '.join(step.split("*")[1:]))

            messages[d['id']] = intents

    with open(dump_f, "w+") as f:
        json.dump({}, f)

    for id in messages.keys():
        for m in messages[id]:

            with open(dump_f) as f:
                old_dump = json.load(f)

            if id in old_dump:
                old_dump[id].append("* " + m)
            else:
                old_dump[id] = ['* {}'.format(m)]

            with open(dump_f, "w+") as f:
                json.dump(old_dump, f)

            mes = "/{}".format(m.strip())
            print(mes)
            agent.compile_message(mes, sender_id=id, summary=summary, dump_interaction=dump_f)

    with open(dump_f) as f:
        interactions = json.load(f)
    
    story_id = 0    

    with open(fine_tune_data_file, "w+") as f:

        for dial in interactions:
            f.write("## story_{}\n".format(story_id))
            for step in interactions[dial]:
                if step[0] == "*":
                    f.write("{}\n".format(step))
                else:
                    if not "action_listen" in step:
                        f.write(" {}\n".format(step))
            story_id += 1
            f.write("\n")

    agent = CookieCutterAgent.load(os.path.join(main_folder_path,agent_folder), 
                               tracker_store=inMemo_tracker, interpreter=None)
    
    agent.fine_tune(training_resource_name=fine_tune_data_file, 
                    validation_resource_name=validation_data_file,  
                    model_path=agent_folder, remove_duplicates=True,
                    augmentation_factor=0, max_history=1)


def train_nlu():
    from rasa_nlu.training_data import load_data
    from rasa_nlu import config
    from rasa_nlu.model import Trainer

    training_data = load_data('data/nlu_training.json')
    trainer = Trainer(config.load("config/nlu_model_config.yml"))
    trainer.train(training_data)
    model_directory = trainer.persist('models/nlu/',
                                      fixed_model_name="current")

    return model_directory

def train_dm(domain_file=str(Path(__file__).parents[0]) + "/config/domain.yml",
                              model_path=str(Path(__file__).parents[0]) + "/models/dialogue",
                              training_data_file=str(Path(__file__).parents[0]) +"/data/story.md",
                              validation_data_file=str(Path(__file__).parents[0]) +"/data/valid.md",
                              epochs=10,
                              batch_size=32,
                              validation_split=0.3,
                              max_history=5,
                              featurization="ents"):


    model_path = choose_featurization(model_path, featurization)

    policy = CookieCutterKerasPolicy()
    ens = CookieCutterSimplePolicyEnsemble([policy])
    agent = CookieCutterAgent(domain_file, policies=ens)


    if os.path.isfile(validation_data_file):
        agent.train(training_data_file=training_data_file,
                    validation_data_file=validation_data_file,
                    epochs=int(epochs),
                    batch_size=int(batch_size),
                    remove_duplicates=False,
                    max_history=int(max_history),
                    augmentation_factor=0
                    )
    else:
        agent.train(resource_name=training_data_file,
                    epochs=int(epochs),
                    batch_size=int(batch_size),
                    validation_split=float(validation_split),
                    remove_duplicates=False,
                    max_history=int(max_history),
                    augmentation_factor=0
                    )

    agent.persist(model_path)
    return agent


if __name__ == '__main__':
    utils.configure_colored_logging(loglevel="INFO")

    parser = argparse.ArgumentParser(
            description='starts the bot')

    parser.add_argument(
            'task',
            choices=["train-nlu", "train-dialogue", "run", "fine-tune", "run_feedback" ],
            help="what the bot should do - e.g. run or train?")

    parser.add_argument('-e', '--epochs', default=10, 
                        help='Epochs for the training')
    parser.add_argument('-b', '--batch_size', default=32, 
                        help='Batch size for the training')
    parser.add_argument('-v', '--validation_split', default=0.2, 
                        help='Validation split')
    parser.add_argument('-max_histo', '--max_history', default=5, 
                        help='Max history to use for the training')
    parser.add_argument('-feat', '--featurization', default="ents", 
                        help='Featurization for training the DM; it'
                             ' can be one of the following ["ents",'
                             ' "usem", "elmo", "bow"]')
    parser.add_argument('-offline', '--offline', default=False, action="store_true", 
                        help='Flag indicating if the bot will run online or not')
    parser.add_argument('-fb', '--feedback', default=False, action="store_true", 
                        help='Flag indicating if the bot will run in feedback mode')
    parser.add_argument('-fb_folder', '--feedback_folder', default="/var/www/feedback/", 
                        help='Directory containing folders for feedback task')
    parser.add_argument('-summary_folder', '--summary_folder', default="retag/summary.json", 
                        help='File containing summarization of retagging task')
    parser.add_argument('-dump_folder', '--dump_folder', default="retag/full_interaction.json", 
                        help='File containing summarization of retagging task')



    task = parser.parse_args().task
    args = parser.parse_args()

    # decide what to do based on first parameter of the script
    if task == "train-nlu":
        train_nlu()
    
    elif task == "train-dialogue":
        train_dm(epochs=args.epochs, batch_size=args.batch_size, 
                 validation_split=args.validation_split, max_history=args.max_history, 
                                                     featurization=args.featurization)
    elif task == "run_feedback":
        run(featurization=args.featurization, feedback=True, 
            server_bot_folder=args.feedback_folder)
    
    elif task == "run":
        online = not args.offline
        run(online=online, featurization=args.featurization, 
            feedback=False)
    
    elif task == "fine-tune":
        compile_and_finetune(summary=args.summary_folder, 
                             dump_folder=args.dump_folder, 
                             featurization=args.featurization)


