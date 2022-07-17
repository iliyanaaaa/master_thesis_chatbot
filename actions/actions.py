# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"
import json
from pathlib import Path
from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa.core.actions.forms import FormAction

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.knowledge_base.storage import InMemoryKnowledgeBase
from rasa_sdk.knowledge_base.actions import ActionQueryKnowledgeBase

import sqlalchemy
import psycopg2
import pandas as pd

USER = 'dev_iliyana'
PASSWORD = 'password'
SERVER = 'localhost'
PORT = '5432'
DATABASE = 'hislsf_chatbot_export'
SQA_CONN_STR = f"postgresql://{USER}:{PASSWORD}@{SERVER}:{PORT}/{DATABASE}"

SQA_CONN_PUB_ENGINE = sqlalchemy.create_engine(SQA_CONN_STR,
                                               connect_args={'options': '-csearch_path=public'})
SQA_CONN_PUB = SQA_CONN_PUB_ENGINE.connect()

PSY_CONN_PUB = psycopg2.connect(
    host=SERVER,
    port=PORT,
    database=DATABASE,
    user=USER,
    password=PASSWORD,
    )
PSY_CONN_PUB.autocommit = True
df = pd.read_sql('Select a from test_table', con=SQA_CONN_PUB)
CLASS_NAMES = df['a'].values.tolist()
df = pd.read_sql('Select types from class_type', con=SQA_CONN_PUB)
CLASS_TYPES = df['types'].values.tolist()


class ActionCheckExistence(Action):
    def name(self) -> Text:
        return "action_check_existence"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        for blob in tracker.latest_message['entities']:
            print(tracker.latest_message)
            if blob['entity'] == 'class_name':
                name = blob['value']
                if name in CLASS_NAMES:
                    df = pd.read_sql('Select * from test_table', con=SQA_CONN_PUB)
                    dispatcher.utter_message(text=f"Yes, {name} is a class name. Find it under {df.iloc[0]['a']}")
                else:
                    dispatcher.utter_message(
                        text=f"I do not recognize {name}, are you sure it is correctly spelled?")
        return []


class ActionGetStartTime(FormAction):
    def name(self) -> Text:
        return "get_start_time_form"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:

        print('required_slots(tracker:Tracker)')
        return ['class_type']

    def submit(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict]:

        dispatcher.utter_message(template="utter_submit")
        return []


# class ActionGetStartTime(Action):
#     def name(self) -> Text:
#         return "action_get_start_time"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#         for blob in tracker.latest_message['entities']:
#             print(tracker.latest_message)
#             dispatcher.utter_message(text=blob['entity'])
#             if blob['entity'] == 'class_name':
#                 class_name = blob['value']
#         if class_name in CLASS_NAMES:
#             dispatcher.utter_message(text=f"Do you wanna know more about the lecture or the exercise of {class_name}?")
#         else:
#             dispatcher.utter_message(
#                 text=f"I do not recognize {class_name}, are you sure it is correctly spelled?")
#         return []


class ActionGetLecturer(Action):
    def name(self) -> Text:
        return "action_lecturer"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        class_name = None
        class_type = None
        for blob in tracker.latest_message['entities']:
            print(tracker.latest_message)
            if blob['entity'] == 'class_name':
                class_name = blob['value']
            elif blob['entity'] == 'class_name':
                class_type = blob['class_type']
        if class_name in CLASS_NAMES:
            df = pd.read_sql('Select * from test_table', con=SQA_CONN_PUB)
            dispatcher.utter_message(text=f"Yes, {class_name} is a class name. Find it under {df.iloc[0]['a']}")
        else:
            dispatcher.utter_message(
                text=f"I do not recognize {class_name}, are you sure it is correctly spelled?")
        return []


class ActionGetMoodleLink(Action):
    def name(self) -> Text:
        return "action_get_moodle_link"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        for blob in tracker.latest_message['entities']:
            print(tracker.latest_message)
            if blob['entity'] == 'class_name':
                name = blob['value']
                if name in CLASS_NAMES:
                    df = pd.read_sql('Select * from test_table', con=SQA_CONN_PUB)
                    dispatcher.utter_message(text=f"Yes, {name} is a class name. Find it under {df.iloc[0]['a']}")
                else:
                    dispatcher.utter_message(
                        text=f"I do not recognize {name}, are you sure it is correctly spelled?")
        return []


class ActionHelloWorld(Action):

    def name(self) -> Text:
        return "action_hello_world"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(text="Hello World!")

        return []
