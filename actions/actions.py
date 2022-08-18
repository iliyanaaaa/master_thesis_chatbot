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
from rasa_sdk.events import SlotSet, EventType
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.knowledge_base.storage import InMemoryKnowledgeBase
from rasa_sdk.knowledge_base.actions import ActionQueryKnowledgeBase

import pandas as pd
import Levenshtein

from actions.db_connections import PSY_CONN_PUB, SQA_CONN_PUB
from actions.sql_queries import get_class_start_time_query, get_available_class_types_by_class_name_query, \
    get_all_classes_info_query, get_lecturer_query, get_location_query, get_moodle_link_query, add_weekday_query, \
    get_class_types_query

PSY_CONN_PUB.autocommit = True
df_class_names = pd.read_sql(get_all_classes_info_query, con=SQA_CONN_PUB)
CLASS_NAMES = df_class_names['class_name'].values.tolist()
df_class_types = pd.read_sql(get_all_classes_info_query, con=SQA_CONN_PUB)
CLASS_TYPES = df_class_types['class_type'].values.tolist()
CLASS_TYPE_MAPPINGS_df = pd.read_sql('Select * from types_of_classes', con=SQA_CONN_PUB)
WEEKDAYS_EN_DE = dict(pd.read_sql('Select * from weekdays order by weekday_eng', con=SQA_CONN_PUB).values)
WEEKDAYS_DE_EN = {y: x for x, y in WEEKDAYS_EN_DE.items()}
CLASS_TYPES_EN_DE = dict(pd.read_sql(get_class_types_query, con=SQA_CONN_PUB).values)
CLASS_TYPES_DE_EN = {y: x for x, y in CLASS_TYPES_EN_DE.items()}

LANG = 'en'

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


class ValidateClassNameTypeForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_class_name_type_form"

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
            class_type = \
                CLASS_TYPE_MAPPINGS_df.loc[CLASS_TYPE_MAPPINGS_df['abbr'] == class_type]['class_type'].values.tolist()[
                    0]
        df = pd.read_sql(get_class_start_time_query % (class_name, class_type), con=SQA_CONN_PUB)
        if df.empty:
            dispatcher.utter_message(text=f"I'm sorry. There is no data about the {class_type} {class_name}")
            return {"class_type": None}
        return {"class_type": class_type}


class ValidateClassNameForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_class_name_form"

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


class AskForVegetarianAction(Action):
    def name(self) -> Text:
        return "action_ask_vegetarian"

    def run(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        dispatcher.utter_message(
            text="Would you like to order a vegetarian pizza?",
            buttons=[
                {"title": "yes", "payload": "/affirm"},
                {"title": "no", "payload": "/deny"},
            ],
        )
        return []


class AskForClassTypeAction(Action):
    def name(self) -> Text:
        return "action_ask_class_type"

    def run(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        class_name = tracker.get_slot('class_name')
        weekday = tracker.get_slot('weekday')
        df_available_class_types = pd.read_sql(get_available_class_types_by_class_name_query % class_name, con=SQA_CONN_PUB)
        available_class_types = df_available_class_types['class_type'].values.tolist()
        if len(available_class_types) > 1:
            dispatcher.utter_message(
                text=f"Which kind of class?",
                buttons=[{"title": p, "payload": p} for p in available_class_types],
            )
        elif len(available_class_types) == 1:
            # todo: Slot is set, but what is the intent or action?
            class_type = available_class_types[0]
            message = choose_action(tracker, class_name, class_type, weekday)
            dispatcher.utter_message(text=message)
            # df = pd.read_sql(get_class_start_time_query % (class_name, available_class_types[0]), con=SQA_CONN_PUB)
            # message = ''
            # for i, row in df.iterrows():
            #     if row['week_day'] is not None:
            #         message += f"The {available_class_types[0]} {class_name} starts at {row['start_time']} \
            #         on {row['week_day']}."
            # dispatcher.utter_message(text=message)
            # text=f"Information about {available_class_types[0]} {class_name} is being loaded.")
            return [SlotSet('class_type', class_type)]
        return []


class ActionGetAnswer(Action):
    def name(self) -> Text:
        return "action_get_answer"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        class_name = tracker.get_slot('class_name')
        class_type = tracker.get_slot('class_type')
        weekday = tracker.get_slot('weekday')
        # intent = tracker.latest_message['intent'].get('name')
        message = choose_action(tracker, class_name, class_type, weekday)
        dispatcher.utter_message(text=message)

        return [SlotSet('class_type', None)]


def return_class_start_time(class_name, class_type, weekday) -> Text:
    print('start return_class_start_time')
    message = ''
    query = get_class_start_time_query % (class_name, class_type)
    if weekday is not None:
        query += add_weekday_query % WEEKDAYS_EN_DE.get(weekday)
    df = pd.read_sql(query, con=SQA_CONN_PUB)
    print(query)
    for i, row in df.iterrows():
        if row['week_day'] is not None:
            message += f"The {CLASS_TYPES_DE_EN.get(class_type)} {class_name} starts at {row['start_time']} " \
                       f"on {WEEKDAYS_DE_EN.get(row['week_day'])}."
    print('the message is', message)
    return message


def return_class_lecturer(class_name, class_type) -> Text:
    print('start return_class_lecturer')
    df = pd.read_sql(get_lecturer_query % (class_name, class_type), con=SQA_CONN_PUB)
    if not df.empty:
        message = f"The lecturer of the {CLASS_TYPES_DE_EN.get(class_type)} {class_name} is {df.iloc[0]['lecturer']}."
    else:
        message = f"I can't find the {CLASS_TYPES_DE_EN.get(class_type)} {class_name} in the database."
    return message


def return_class_location(class_name, class_type, weekday) -> Text:
    print('start return_class_location')
    query = get_location_query % (class_name, class_type)
    if weekday is not None:
        query += add_weekday_query % weekday
    df = pd.read_sql(query, con=SQA_CONN_PUB)
    if not df.empty:
        message = f"The {CLASS_TYPES_DE_EN.get(class_type)} {class_name} takes place in {df.iloc[0]['room']} {df.iloc[0]['floor'].trim()}," \
                  f"{df.iloc[0]['building']}, {df.iloc[0]['facility']}. The address is {df.iloc[0]['address']}."
    else:
        message = f"I can't find the {CLASS_TYPES_DE_EN.get(class_type)} {class_name} in the database."
    return message


def return_class_moodle_link(class_name, class_type, weekday) -> Text:
    print('start return_class_moodle_link')
    query = get_moodle_link_query % (class_name, class_type)
    if weekday is not None:
        query += add_weekday_query % weekday
    df = pd.read_sql(query, con=SQA_CONN_PUB)
    if not df.empty:
        if df.iloc[0]['hyperlink'] is not None:
            message = f"The moodle link for the {CLASS_TYPES_DE_EN.get(class_type)} {class_name} is {df.iloc[0]['hyperlink']}."
        else:
            message = f"There is no data about the moodle link for the {class_type} {class_name}."
    else:
        message = f"I can't find the {CLASS_TYPES_DE_EN.get(class_type)} {class_name} in the database."
    return message


def choose_action(tracker, class_name, class_type, weekday):
    reversed_events = list(reversed(tracker.events))
    intent_name = ''
    message = ''
    for event in reversed_events:
        if 'parse_data' in event.keys():
            intent_name = event['parse_data']['intent']['name']
            print(intent_name)
            if intent_name != 'inform':
                break
    print('Outside of for loop, intent is', intent_name)
    if intent_name == 'ask_class_start_time':
        message = return_class_start_time(class_name, class_type, weekday)
    elif intent_name == 'ask_class_lecturer':
        message = return_class_lecturer(class_name, class_type)
    elif intent_name == 'ask_class_location':
        message = return_class_location(class_name, class_type, weekday)
    elif intent_name == 'ask_class_moodle_link':
        message = return_class_moodle_link(class_name, class_type, weekday)
    return message

class ActionGetLecturer(Action):
    def name(self) -> Text:
        return "action_get_lecturer"

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
            df = pd.read_sql(get_lecturer_query, con=SQA_CONN_PUB)
            dispatcher.utter_message(text=f"The lecturer of the {class_type} {class_name} is {df.iloc[0]['lecturer']}")
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
