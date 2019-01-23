
This repo contains my master thesis project. The first half of the project is a collaborative effort with Federico Giannoni (https://github.com/djanno), one of the best student and friend I've ever met. 

It is composed by a new framework which aims to build
end-to-end dialogue system in an automatic way, starting from a catalogue and leveraging MachineTo-Machine interactions, similarly to what done in [https://arxiv.org/abs/1801.04871]. Additionally, inspired by several works on
the usage of feedback in building dialogue systems, I also designed two experiments to collect explicit
feedbacks about errors in real conversations. These feedbacks are then used from the framework to
automatically detect errors during a conversation with an agent generated through the framework
itself.

The repo is organized in two main sub-folders:
* Catalog2Dialogue: Contains the code of Cookie-Cutter, the framework for automatically bootstrapping dialogue agents.
* Automatic error discovery on dialogue agents: Contains the code used for the automatic error discovery experiments I've run. 

The master thesis can be found in the first page and I highly suggests to follow it in order to understand both the projects. 

Since both projects are under NDA the data used are not provided.

# Catalog2Dialogue

This is the first half of my master thesis project. 

The first instance of this framework is the result of a collaborative effort with Federico Giannoni1,
and it has been designed and partly developed during an internship at VUI,inc.

The objective is to rapidly bootstrap a task-oriented dialogue system in a specific domain
and for specific tasks the developer wants its virtual assistant to be able to carry on. We want this
framework being able to work in any domain and bootstrap a dialogue agent in absence of dialogue
data. Instead, the framework will start from a catalogue, representing the domain of interest, (e.g
MySQL database) and will guide the developer through the bootstrapping of all the components of a
data-driven dialogue system, with a minimum manual effort.



Cookie-Cutter, in order to build the final data-driven dialogue agent, guide the developer through
these steps:
1. Preparation
	1. The developer, through a GUI uploads a dump of the database.
	2. The developer defines the Task structure, populating all the involved frames with all the information needed (example file: movies.json, restaurant.json)
	3. The developer chooses the training setting of the data driven DM between the three options: entities only, intents + entities, Sentence Embedding + entities.
2. Data Generation
	1. A main script run, starting to generate Goals and Tasks of Frames. Goals are fed to the user simulator and Frames to the DM.
	2. A Trainer is instantiated, according to the settings indicated by the user, and is fed to a singleton instance of the Interaction Manager.
	3. The just generated IM is shared between DM and User Simulator.
	4. The Machine-to-Machine interaction begins in order to generate N training dialogues under the form of story files. A 30% of these dialogues will be kept as validation set, the remaining 70% as training set.
	5. The Trainer instance, during the interaction, populates all the files needed by the RASA framework
3. Data Feeding
	1. Once the simulation finishes, a data folder is filled with the domain file, the custom actions python code and the story files (data folder). Additionally, also sentence embeddings can be provided
	2. The Trainer calls specific routines to feed those data to RASA, and a data-driven DM is the output of the overall process.

In order to have diversity in the generated data, during the generation process Cookie-Cutter automatically manage the User Simulator profile, starting from a full collaborative user till a noncooperative user.

A better explanation and overview of all the components and processed implemented in Cooie-Cutter can be found on the master thesis. 

# Automatic-Error-Discovery-on-Dialogue-Agents

This is the second half of my master thesis project. 

In this project I had to design and implement the back-end and the front-end for two different labelling scenarios involving testers into an interaction with a spoken dialogue system automatically produced through the Cookie-Cutter framework.

The tester was asked to reach a specific goal and, in case the goal was not reached, he was asked to provide the error category among the three different categories [NLU, DM, BOTH]. The objective was to gather data about errors happening in real interactions with task-oriented dialogue agents and, with such data, build ML/AI models to understand, at each turn of the conversation, if the agent made an error. 

During the interaction with the BOT the back-end collects information such as:
* Dialogue State
* NLU module outputs [entities + intents + confidence scores]
* DM module outputs [actions + confidence scores] 
* User Text

Based on these information I built featurizers which extracts the following features:
* Entities vector: Binary vector indicating which entities have been recognized in the featurized*
turn.
* System Belief vector: Binary vector indicating all the slots recognized so far by the system.
* Actions vector: Binary vector indicating all the actions predicted by the system in that turn.
* User text vector: Vector representing the user text under the form of Bag of Words. It is
a vector of size N, where N is the size of the vocabulary used by the user, where each element
corresponds to a word in the vocabulary and it works as a counter of that word in the current
turn.
* Confidence vector: This vector embeds the confidence scores of either the NLU or the DM
module, additionally we also offer a setting in which both confidences are concatenated.
* DB consistency vector: This is a binary vector with the same length of the entities recognizable by the system. Each bit corresponds to an entity and if its value is 1 it means that the
entity recognized by the system is available in the database, otherwise its value is 0.

Based on these features I built these models:
* Random Classifier
* Threshold Classifier
* Majority Model
* Linear SVM
* Logistic Regression
* Isolation Forest
* Multi-layer Perceptron
* Neural Anomaly Detector

A better explanation of both experimental scenarios, features and models can be found in the thesis work.


Since this work is under NDA, the data are not provided. 