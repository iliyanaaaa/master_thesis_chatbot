# Humbot: University Chatbot
A prototype of a University Chatbot created with Python

## Author
Iliyana Tarpova, business informatics student at Humboldt University of Berlin


## Project description
This project is part of the author's master thesis. Its aim is to prove whether 
the University System Agnes of Humboldt University of Berlin is suitable for an AI implementation.

This project is a prototype of a Question-Answering system for the University of Berlin.
It is developed in the form of a Chatbot, named Humbot.

The underlying architecture for Humbot is [Rasa, v.3](https://rasa.com/), and it is used 
for Natural Language Understanding and Dialogue Management.

Humbot gets as input a question about a university course and outputs an answer.

## Features

It is able to understand and answer questions from a predefined domain. These questions include data about
* the start time of a course
* the lecturer of a course
* the location of a course
* the Moodle link to a course
* the course description
* the target group of a course
* the exam type of a course
* whether a registration is necessary for a course

The courses for which information is available can be found in the file *data/csv_exports/classes_to_choose_from.csv*

The project can either be connected to the University database for access to the full University data or to local files 
which contain only the needed information for the prototype. By default, this project connects to the local files.

Currently, Humbot is able to understand user questions in English, while class types and weekdays in both English and German.
It struggles with extracting class names which consist of more than two words, but recognizes shorter ones with almost perfect accuracy.

This Chatbot could be further developed to answer more complex user requests and deliver information on other aspects 
of the student life. 

## Technologies
* Python 3.8
* Rasa 3.2
* PostgreSQL 14

## Installation    

To to able to use Humbot, please create a virtual environment and install all 
requirements for the Chatbot there.

```bash
virtualenv <env_name>
<env_name>\Scripts\activate
pip install -r requirements.txt
```

The first time using Rasa, the following command should be run to initialize the project

```bash
python -m rasa init 
```

## Usage

After the project is initialized and all required packages are installed, the Chatbot can be started with the following command in the created virtual environment

```bash
rasa run actions
```

![img.png](images/rasa_run_actions.png)

In a new Command Prompt window activate the virtual environment once again and run the following command

```bash
rasa shell
```

![img.png](images/rasa_shell.png)

This will start the program and the user will be asked to input a question. Then the respective answer will be presented.

## Examples of use

![img.png](images/examples.png)

## Train the model

A new model can be trained with the following command

```bash
rasa train
```

For the development, Rasa interactive tool can be used to gain a better insight of 
the model decisions. There the developer can check if the intents and entities get 
recognized and correct the model when mistakes are made. Further, the conversation 
flow can be influenced and new user stories can be created. Activate the interactive tool with the following command:

```bash
rasa interactive
```

## References

Rasa. (2019). Rasa: Open source conversational AI. Retrieved from Rasa.com website: https://rasa.com/