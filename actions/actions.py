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



class ActionCheckExistence(Action):
    knowledge = Path("data/class_name.txt").read_text().split("\n")

    def name(self) -> Text:
        return "action_check_existence"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        for blob in tracker.latest_message['entities']:
            print(tracker.latest_message)
            if blob['entity'] == 'class_name':
                name = blob['value']
                if name in self.knowledge:
                    df = pd.read_sql('Select * from test_table', con=SQA_CONN_PUB)
                    df.iloc[0]['a']
                    dispatcher.utter_message(text=f"Yes, {name} is a class name. Find it under {df.iloc[0]['a']}")
                else:
                    dispatcher.utter_message(
                        text=f"I do not recognize {name}, are you sure it is correctly spelled?")
        return []


class ActionGetStartTime(Action):
    knowledge = Path("data/class_name.txt").read_text().split("\n")

    def name(self) -> Text:
        return "action_get_start_time"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        for blob in tracker.latest_message['entities']:
            print(tracker.latest_message)
            if blob['entity'] == 'class_name':
                name = blob['value']
                if name in self.knowledge:
                    dispatcher.utter_message(text=f"The class {name} starts at 9 am.")
                else:
                    dispatcher.utter_message(
                        text=f"I do not recognize {name}, are you sure it is correctly spelled?")
        return []


class ActionGetMoodleLink(Action):
    knowledge = Path("data/class_name.txt").read_text().split("\n")

    def name(self) -> Text:
        return "action_get_moodle_link"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        for blob in tracker.latest_message['entities']:
            print(tracker.latest_message)
            if blob['entity'] == 'class_name':
                name = blob['value']
                if name in self.knowledge:
                    df = pd.read_sql('Select * from test_table', con=SQA_CONN_PUB)
                    df.iloc[0]['a']
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
