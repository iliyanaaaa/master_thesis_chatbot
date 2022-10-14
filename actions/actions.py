# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"
from typing import Any, Text, Dict, List

import torch

from rasa_sdk import Tracker, FormValidationAction
from rasa.core.actions.forms import FormAction
from rasa_sdk.types import DomainDict

from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet, EventType
from rasa_sdk.executor import CollectingDispatcher

from io import StringIO
from html.parser import HTMLParser
# import torch

import pandas as pd
import Levenshtein
from transformers import AutoTokenizer, AutoModelForQuestionAnswering

from actions.db_connections import PSY_CONN_PUB, SQA_CONN_PUB
from actions.sql_queries import get_class_start_time_query, get_available_class_types_by_class_name_query, \
    get_all_classes_info_query, get_lecturer_query, get_location_query, get_moodle_link_query, add_weekday_query, \
    get_class_types_query, get_weekday_en_de, get_class_is_about, get_types_of_classes, \
    add_class_type_query, class_info_view_txt_query_class_name

MODE = 'local_csv'  # 'local_csv' 'database'
sqa_con = SQA_CONN_PUB

PSY_CONN_PUB.autocommit = True

VARIABLES_DICT = {'class_types': 'class_type',
                  'all_classes': ' class_name, class_type',
                  'start_time': ' class_name, class_type, start_time, week_day',
                  'lecturer': ' lecturer, week_day',
                  'location': ' room, floor , building , facility , address, week_day',
                  'moodle_link': 'hyperlink, week_day',
                  'class_is_about': 'txt'}


def perform_query(mode, looking_for, class_name=None, class_type=None, weekday=None, con=None):
    if mode == 'database' and con is not None:
        if looking_for == 'all_classes':
            query = get_all_classes_info_query
        elif looking_for == 'types_of_classes':
            query = get_types_of_classes
        elif looking_for == 'weekdays':
            query = get_weekday_en_de
        else:
            variables = VARIABLES_DICT.get(looking_for)
            query = class_info_view_txt_query_class_name % (variables, class_name)
            if class_type is not None:
                query += add_class_type_query % class_type
            if weekday is not None:
                query += add_weekday_query % weekday
        print('Final query is', query)
        df = pd.read_sql(query, con=con)
    elif mode == 'local_csv':
        if looking_for == 'weekdays':
            df = pd.read_csv('C:/Users/tarpo/PycharmProjects/master_thesis_chatbot/data/csv_exports/weekdays.csv')
        elif looking_for == 'types_of_classes':
            df = pd.read_csv('C:/Users/tarpo/PycharmProjects/master_thesis_chatbot/data/csv_exports/types_of_classes.csv')
        else:
            df = pd.read_csv('C:/Users/tarpo/PycharmProjects/master_thesis_chatbot/data/csv_exports/class_info_view_txt.csv')
            variables_str = VARIABLES_DICT.get(looking_for)
            variables = variables_str.split(',')
            variables = [x.strip(' ') for x in variables]
            print('class name:', class_name, 'class type:', class_type, 'week day:', weekday)
            if class_name is not None:
                df = df[(df['class_name'] == class_name)]
            if class_type is not None:
                df = df[(df['class_type'] == class_type)]
            if weekday is not None:
                df = df[(df['week_day'] == weekday)]
            df = df[variables].drop_duplicates(ignore_index=True)

    return df


df_class_names = perform_query(MODE, 'all_classes', con=sqa_con)
CLASS_NAMES = df_class_names['class_name'].values.tolist()
CLASS_TYPES = df_class_names['class_type'].values.tolist()
CLASS_TYPE_MAPPINGS_df = perform_query(MODE, 'types_of_classes', con=sqa_con)
WEEKDAYS_EN_DE = dict(perform_query(MODE, 'weekdays', con=sqa_con).values)
WEEKDAYS_DE_EN = {y: x for x, y in WEEKDAYS_EN_DE.items()}
# CLASS_TYPES_EN_DE = dict(pd.read_sql(get_class_types_query, con=SQA_CONN_PUB).values)
CLASS_TYPES_DE_EN = {"Seminar": "seminar",
                     "Übung": "exercise",
                     "Vorlesung": "lecture",
                     "Grundkurs": "ground course",
                     "Sprachkurs": "language course",
                     "Hauptseminar": "main seminar",
                     "Basiskurse":"base course",
                     "Colloquium":"colloquim",
                     "Forschungsseminar":"practice seminar",
                     "Integrierter Theorie- und Praxiskurs":"integrated theorie and practice course",
                     "Klausurenkurs":"exam course",
                     "Kolloquium":"colloquim",
                     "Masterseminar":"master seminar",
                     "Oberseminar":"senior seminar",
                     "Praktikum":"internship",
                     "Praxisorientierte Lehrveranstaltung":"Practice-oriented course",
                     "Projektseminar":"project seminar",
                     "Proseminar":"pro seminar",
                     "Seminar/Hauptseminar":"seminar/main seminar",
                     "Seminar/Proseminar":"seminar/pro seminar",
                     "Studienprojekt":"study project",
                     "Tutorium":"tutorial",
                     "Vertiefungskurse":"advanced course",
                     "Vorlesung/Grundkurs":"lecture/ground course",
                     "Vorlesung/Übung":"lecture/exercise"
                     }
CLASS_TYPES_EN_DE = {y: x for x, y in CLASS_TYPES_DE_EN.items()}

LANG = 'en'

electra_tokenizer = AutoTokenizer.from_pretrained("valhalla/electra-base-discriminator-finetuned_squadv1")
electra_model = AutoModelForQuestionAnswering.from_pretrained("valhalla/electra-base-discriminator-finetuned_squadv1")


class MLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.text = StringIO()

    def handle_data(self, d):
        self.text.write(d)

    def get_data(self):
        return self.text.getvalue()


def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()


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

        print('start validating class type name')
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

        print('start validating class type:', class_type)
        print('class type in CLASS_TYPES:', class_type in CLASS_TYPES_EN_DE.keys())
        class_name = tracker.get_slot('class_name')
        if class_type in CLASS_TYPES_EN_DE.keys():
            class_type = CLASS_TYPES_EN_DE.get(class_type)
        elif class_type not in CLASS_TYPES:
            similarity_perc = [Levenshtein.jaro(class_type.lower(), s.lower()) for s in CLASS_TYPES]
            if max(similarity_perc) < 0.7:
                dispatcher.utter_message(text=f"I don't recognize that class type. You could choose from "
                                              f"lecture/exercise/seminar")
                return {"class_type": None}
            else:
                most_similar_index = similarity_perc.index(max(similarity_perc))
                class_type = CLASS_TYPES[most_similar_index]
        # if class_type not in ['lecture', 'exercise', 'seminar']:
        #     class_type = \
        #         CLASS_TYPE_MAPPINGS_df.loc[CLASS_TYPE_MAPPINGS_df['abbr'] == class_type][
        #             'class_type_de'].values.tolist()[
        #             0]
        df = perform_query(mode=MODE, looking_for='start_time', class_name=class_name,
                           class_type=class_type, con=sqa_con)
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

        print('start validating class name')
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


class AskForClassTypeAction(Action):
    def name(self) -> Text:
        return "action_ask_class_type"

    def run(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        class_name = tracker.get_slot('class_name')
        weekday = tracker.get_slot('weekday')
        df_available_class_types = perform_query(mode=MODE, looking_for='class_types',
                                                 class_name=class_name, con=sqa_con)
        available_class_types = df_available_class_types['class_type'].values.tolist()
        if len(available_class_types) > 1:
            dispatcher.utter_message(
                text=f"Which kind of class?",
                buttons=[{"title": CLASS_TYPES_DE_EN.get(p), "payload": p} for p in available_class_types],
            )
        elif len(available_class_types) == 1:
            # todo: Slot is set, but what is the intent or action?
            class_type = available_class_types[0]
            print('in action_ask_class_type class type is', class_type)
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
    weekday_string = ''
    if weekday is not None:
        weekday_string = ' on ' + weekday
        weekday = WEEKDAYS_EN_DE.get(weekday)
    df = perform_query(mode=MODE, looking_for='start_time', class_name=class_name,
                       class_type=class_type, weekday=weekday, con=sqa_con)
    if df.empty:
        class_type_string = '' if class_type is None else CLASS_TYPES_DE_EN.get(class_type)
        message = f"I'm sorry, there is no data about the starting time of the {class_type_string} {class_name}"
        message += weekday_string
    else:
        print(df.head())
        for i, row in df.iterrows():
            if row['week_day'] is not None:
                print('the class type is', class_type)
                print('the class type in english is', CLASS_TYPES_DE_EN.get(class_type))
                if i == 0:
                    message += f"The {CLASS_TYPES_DE_EN.get(class_type)} {class_name} starts at {row['start_time']} " \
                           f"on {WEEKDAYS_DE_EN.get(row['week_day'])}"
                else:
                    message += f" and at {row['start_time']} on {WEEKDAYS_DE_EN.get(row['week_day'])}"
    print('the message is', message)
    return message + '.'


def return_class_lecturer(class_name, class_type) -> Text:
    print('start return_class_lecturer')
    df = perform_query(mode=MODE, looking_for='lecturer', class_name=class_name,
                       class_type=class_type, con=sqa_con)
    if df.empty or df.iloc[0]['lecturer'] is None:
        class_type_string = '' if class_type is None else CLASS_TYPES_DE_EN.get(class_type)
        message = f"I'm sorry, there is no data about the lecturer of the {class_type_string} {class_name}"
    else:
        message = f"The lecturer of the {CLASS_TYPES_DE_EN.get(class_type)} {class_name} is {df.iloc[0]['lecturer']}."
    return message


def return_class_location(class_name, class_type, weekday) -> Text:
    print('start return_class_location')
    weekday_string = ''
    if weekday is not None:
        weekday_string = ' on ' + weekday
        weekday = WEEKDAYS_EN_DE.get(weekday)
    df = perform_query(mode=MODE, looking_for='location', class_name=class_name,
                       class_type=class_type, weekday=weekday, con=sqa_con)
    if df.empty:
        class_type_string = '' if class_type is None else CLASS_TYPES_DE_EN.get(class_type)
        message = f"I'm sorry, there is no data about the location of the {class_type_string} {class_name}"
        message += weekday_string
    else:
        if weekday_string == '' and df.iloc[0]['week_day'] is not None:
            weekday_string = ' on ' + WEEKDAYS_DE_EN.get(df.iloc[0]['week_day'])
        message = f"The {CLASS_TYPES_DE_EN.get(class_type)} {class_name} {weekday_string} takes place " \
                  f"in {df.iloc[0]['room']} {df.iloc[0]['floor'].strip()}, " \
                  f"{df.iloc[0]['building']}, {df.iloc[0]['facility']}. The address is {df.iloc[0]['address']}."
    return message


def return_exam_type(class_name) -> Text:
    print('start return_exam_type')
    df = perform_query(mode=MODE, looking_for='class_is_about', class_name=class_name, con=sqa_con)
    if not df.empty:
        message = strip_tags(df.iloc[0]['txt'])
    else:
        message = f"I can't find information about {class_name} in the database."
    return message


def return_open_question(class_name, tracker) -> Text:
    print('start return_open_question for class name ', class_name)
    df = perform_query(mode=MODE, looking_for='class_is_about', class_name=class_name, con=sqa_con)
    if df.empty:
        message = f"I'm sorry, there is no data on this topic about {class_name} in the database."
    else:
        context = strip_tags(df.iloc[0]['txt'])
        question = tracker.latest_message['text']
        message = qa(question, context, electra_model, electra_tokenizer)
    return message


def return_class_moodle_link(class_name, class_type, weekday) -> Text:
    print('start return_class_moodle_link')
    weekday_string = ''
    if weekday is not None:
        weekday_string = ' on ' + weekday
        weekday = WEEKDAYS_EN_DE.get(weekday)
    df = perform_query(mode=MODE, looking_for='moodle_link', class_name=class_name,
                       class_type=class_type, weekday=weekday, con=sqa_con)
    if df.empty or df.iloc[0]['hyperlink'] is None:
        class_type_string = '' if class_type is None else CLASS_TYPES_DE_EN.get(class_type)
        message = f"I'm sorry, there is no data about the moodle link of the {class_type_string} {class_name}"
        message += weekday_string
    else:
        message = f"The moodle link for the {CLASS_TYPES_DE_EN.get(class_type)} {class_name} {weekday_string} is {df.iloc[0]['hyperlink']}."
    return message


def choose_action(tracker, class_name, class_type, weekday):
    reversed_events = list(reversed(tracker.events))
    intent_name = ''
    message = ''
    for event in reversed_events:
        if 'parse_data' in event.keys():
            intent_name = event['parse_data']['intent']['name']
            if intent_name != 'inform':
                break
    print('Intent is ', intent_name)
    if intent_name == 'ask_class_start_time':
        message = return_class_start_time(class_name, class_type, weekday)
    elif intent_name == 'ask_class_lecturer':
        message = return_class_lecturer(class_name, class_type)
    elif intent_name == 'ask_class_location':
        message = return_class_location(class_name, class_type, weekday)
    elif intent_name == 'ask_class_moodle_link':
        message = return_class_moodle_link(class_name, class_type, weekday)
    elif intent_name == 'ask_exam_type':
        message = return_exam_type(class_name)
    elif intent_name == 'ask_open_question':
        message = return_open_question(class_name, tracker)
    return message


def qa(question, answer_text, model, tokenizer):
    inputs = tokenizer.encode_plus(question, answer_text, add_special_tokens=True, return_tensors="pt")
    input_ids = inputs["input_ids"].tolist()[0]

    text_tokens = tokenizer.convert_ids_to_tokens(input_ids)
    # print(text_tokens)
    outputs = model(**inputs)
    answer_start_scores = outputs.start_logits
    answer_end_scores = outputs.end_logits

    answer_start = torch.argmax(
        answer_start_scores
    )  # Get the most likely beginning of answer with the argmax of the score
    answer_end = torch.argmax(answer_end_scores) + 1  # Get the most likely end of answer with the argmax of the score

    answer = tokenizer.convert_tokens_to_string(tokenizer.convert_ids_to_tokens(input_ids[answer_start:answer_end]))

    # Combine the tokens in the answer and print it out.""
    answer = answer.replace("#", "")

    return answer
