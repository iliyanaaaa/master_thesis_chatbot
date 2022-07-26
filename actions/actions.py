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
from rasa_sdk.forms import FormValidationAction
from rasa_sdk import Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict

from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.knowledge_base.storage import InMemoryKnowledgeBase
from rasa_sdk.knowledge_base.actions import ActionQueryKnowledgeBase

import sqlalchemy
import psycopg2
import pandas as pd
import Levenshtein

from actions.sql_queries import get_class_start_time

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
df_class_names = pd.read_sql('Select a from test_table', con=SQA_CONN_PUB)
CLASS_NAMES = df_class_names['a'].values.tolist()
df_class_types = pd.read_sql('Select types from class_type', con=SQA_CONN_PUB)
CLASS_TYPES = df_class_types['types'].values.tolist()
CLASS_TYPE_MAPPINGS_df = pd.read_sql('Select * from types_of_classes', con=SQA_CONN_PUB)
# CLASS_TYPE_MAPPINGS = df_class_type_mappings['types'].values.tolist()


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


class ValidateSimpleClassForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_simple_class_form"

    def validate_class_name(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `class_name` value."""

        if slot_value not in CLASS_NAMES:
            similarity_perc = [Levenshtein.jaro(slot_value.lower(), s.lower()) for s in CLASS_NAMES]
            if max(similarity_perc) < 0.7:
                dispatcher.utter_message(text=f"I don't recognize this class name. Could you try again please?")
                return {"class_name": None}
            else:
                most_similar_index = similarity_perc.index(max(similarity_perc))
                slot_value = CLASS_NAMES[most_similar_index]
                return {"class_name": slot_value}
        return {"class_name": slot_value}

    def validate_class_type(
        self,
        class_type: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `class_type` value."""
        class_name = tracker.get_slot('class_name')
        if class_type not in CLASS_TYPES:
            similarity_perc = [Levenshtein.jaro(class_type.lower(), s.lower()) for s in CLASS_TYPES]
            if max(similarity_perc) < 0.7:
                dispatcher.utter_message(text=f"I don't recognize that class type. You could choose from "
                                              f"lecture/exercise/seminar")
                return {"class_type": None}
            else:
                most_similar_index = similarity_perc.index(max(similarity_perc))
                class_type = CLASS_TYPES[most_similar_index]
        if class_type not in ['lecture', 'exercise', 'seminar']:
            class_type = CLASS_TYPE_MAPPINGS_df.loc[CLASS_TYPE_MAPPINGS_df['abbr'] == class_type]['class_type'].values.tolist()[0]
        df = pd.read_sql(get_class_start_time % (class_name, class_type), con=SQA_CONN_PUB)
        if df.empty:
            dispatcher.utter_message(text=f"I'm sorry. There is no data about the {class_type} {class_name}")
            return {"class_type": None}
        dispatcher.utter_message(text=f"The {class_type} {class_name} starts at {df.iloc[0]['b']} am.")
        return {"class_type": class_type}


# class ActionGetStartTime(FormAction):
#     def name(self) -> Text:
#         return "get_start_time_form"
#
#     @staticmethod
#     def required_slots(tracker: Tracker) -> List[Text]:
#
#         print('required_slots(tracker:Tracker)')
#         return ['class_type']
#
#     def submit(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict]:
#
#         dispatcher.utter_message(template="utter_submit")
#         return []


class ActionGetStartTime(Action):
    def name(self) -> Text:
        return "action_get_start_time"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        class_name = next(tracker.get_latest_entity_values('class_name'), None)
        print(class_name)
        for blob in tracker.latest_message['entities']:
            print(tracker.latest_message)
            dispatcher.utter_message(text=blob['entity'])
            if blob['role'] == 'class_name':
                class_name = blob['value']
        if class_name in CLASS_NAMES:
            message_title = f"Do you wanna know more about the lecture or the exercise of {class_name}?"
            dispatcher.utter_message(text=message_title)

            entities = tracker.latest_message.get("entities", [])
            entities = {e["entity"]: e["value"] for e in entities}
            buttons = []
            for class_type in ['lecture', 'exercise', 'seminar']:
                buttons.append(
                    {"title": class_type, "payload": f"/start_time_{class_type}"}
                )

            buttons.append({"title": "Something else", "payload": "/out_of_scope"})

            dispatcher.utter_message(text=message_title, buttons=buttons)
        else:
            dispatcher.utter_message(
                text=f"I do not recognize {class_name}, are you sure it is correctly spelled?")
        return [SlotSet('class_name', class_name)]


# class ActionGetStartTimeLecture(Action):
#     def name(self) -> Text:
#         return "action_get_start_time_lecture"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#         class_type = next(tracker.get_latest_entity_values('class_type'), None)
#         class_name = tracker.get_slot('class_name')
#
#         dispatcher.utter_message(text=f"The lecture {class_name} starts at 10 am.")
#         return []


class ActionGetStartTimeWithClassType(Action):
    def name(self) -> Text:
        return "action_get_start_time_with_class_type"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        class_type = next(tracker.get_latest_entity_values('class_type'), None)
        class_name = tracker.get_slot('class_name')
        print('Class name from slot', class_name)
        for blob in tracker.latest_message['entities']:
            print(tracker.latest_message)
            dispatcher.utter_message(text=blob['entity'])
            if blob['role'] == 'class_name':
                class_name = blob['value']
                print('Class name from role', class_name)
            if blob['role'] == 'class_type':
                class_type = blob['value']
        print('Class type from role', class_type)
        if class_name in CLASS_NAMES:
            if class_type in CLASS_TYPES:
                dispatcher.utter_message(text=f"The {class_type} {class_name} starts at 9 am.")
        else:
            dispatcher.utter_message(
                text=f"I do not recognize the {class_type} {class_name}, are you sure it is correctly spelled?")
        return []


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
