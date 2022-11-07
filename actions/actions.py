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

import pandas as pd
import Levenshtein
from transformers import AutoTokenizer, AutoModelForQuestionAnswering

from actions.db_connections import PSY_CONN_PUB, SQA_CONN_PUB
from actions.sql_queries import get_all_classes_info_query, add_weekday_query, \
    get_weekday_en_de, get_types_of_classes, \
    add_class_type_query, class_info_view_txt_query_class_name

# choose the mode for the database configuration
# 1) 'database': connects to the university database and fetches the information from there
# 2) 'local_csv': has access to a local csv file that contains limited data

MODE = 'local_csv'

# absolute path to the project
project_path = 'C:/Users/tarpo/PycharmProjects/master_thesis_chatbot/'

# path to the folder with csv files
csv_file_folder_path = 'data/csv_exports/'

# connect to the database
if MODE == 'database':
    sqa_con = SQA_CONN_PUB
else:
    sqa_con = None

PSY_CONN_PUB.autocommit = True

# dictionary that defines which fields should be delivered from the DB/csv file
# according to what is searched
VARIABLES_DICT = {'class_types': 'class_type',
                  'all_classes': ' class_name, class_type',
                  'start_time': ' class_name, class_type, start_time, week_day',
                  'lecturer': ' lecturer, week_day',
                  'location': ' room, floor , building , facility , address, week_day',
                  'moodle_link': 'hyperlink, week_day',
                  'open_question': 'txt'}


def perform_query(mode, looking_for, class_name=None, class_type=None, weekday=None, con=None) -> pd.DataFrame:
    """
    Method that fetches the needed information from the database/csv file

    :param mode: defines whether the DB or the csv file should be used
    :param looking_for: defines what data the query should deliver. The value should be from
    the keys of the VARIABLES_DICT dictionary
    :param class_name: name of the class if present
    :param class_type: type of the class if present
    :param weekday: weekday if present
    :param con: DB connection if present

    :return: a data frame containing the result from the query
    """
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
        df = pd.read_sql(query, con=con)
    elif mode == 'local_csv':
        if looking_for == 'weekdays':
            df = pd.read_csv(project_path + csv_file_folder_path + 'weekdays.csv')
        elif looking_for == 'types_of_classes':
            df = pd.read_csv(project_path + csv_file_folder_path + 'types_of_classes.csv')
        else:
            df = pd.read_csv(project_path + csv_file_folder_path + 'class_info_view_txt.csv')
            variables_str = VARIABLES_DICT.get(looking_for)
            variables = variables_str.split(',')
            variables = [x.strip(' ') for x in variables]

            if class_name is not None:
                df = df[(df['class_name'] == class_name)]
            if class_type is not None:
                df = df[(df['class_type'] == class_type)]
            if weekday is not None:
                df = df[(df['week_day'] == weekday)]

            df = df[variables].drop_duplicates(ignore_index=True)

    return df


# define global variables
df_class_names = perform_query(MODE, 'all_classes', con=sqa_con)

# list of all class names available for the scope of the project
CLASS_NAMES = list(set(df_class_names['class_name'].values.tolist()))
# list of all class types available for the scope of this project
CLASS_TYPES = list(set(df_class_names['class_type'].values.tolist()))

# define class type mappings (i.e. VL -> Vorlesung -> lecture)
CLASS_TYPE_MAPPINGS_df = perform_query(MODE, 'types_of_classes', con=sqa_con)

# define weekday mappings for en -> de translation and vice versa
WEEKDAYS_EN_DE = dict(perform_query(MODE, 'weekdays', con=sqa_con).values)
WEEKDAYS_DE_EN = {y: x for x, y in WEEKDAYS_EN_DE.items()}

# define class type mappings for en -> de translation and vice versa
CLASS_TYPES_DE_EN = {"Seminar": "seminar",
                     "Übung": "exercise",
                     "Vorlesung": "lecture",
                     "Grundkurs": "ground course",
                     "Sprachkurs": "language course",
                     "Hauptseminar": "main seminar",
                     "Basiskurse": "base course",
                     "Colloquium": "colloquim",
                     "Forschungsseminar": "practice seminar",
                     "Integrierter Theorie- und Praxiskurs": "integrated theorie and practice course",
                     "Klausurenkurs": "exam course",
                     "Kolloquium": "colloquim",
                     "Masterseminar": "master seminar",
                     "Oberseminar": "senior seminar",
                     "Praktikum": "practive",
                     "Praxisorientierte Lehrveranstaltung": "Practice-oriented course",
                     "Projektseminar": "project seminar",
                     "Proseminar": "pro seminar",
                     "Seminar/Hauptseminar": "seminar/main seminar",
                     "Seminar/Proseminar": "seminar/pro seminar",
                     "Studienprojekt": "study project",
                     "Tutorium": "tutorial",
                     "Vertiefungskurse": "advanced course",
                     "Vorlesung/Grundkurs": "lecture/ground course",
                     "Vorlesung/Übung": "lecture/exercise"
                     }
CLASS_TYPES_EN_DE = {y: x for x, y in CLASS_TYPES_DE_EN.items()}

# get question answering model ELECTRA from the transformers package
electra_tokenizer = AutoTokenizer.from_pretrained("valhalla/electra-base-discriminator-finetuned_squadv1")
electra_model = AutoModelForQuestionAnswering.from_pretrained("valhalla/electra-base-discriminator-finetuned_squadv1")


# Clean the fields that contain HTML syntax
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


# validation of the class_name_type_form
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
        """
        A method to validate the input for entity class name.
        First it checks if the entity is present in the global variable CLASS_NAMES.
            If it is, it is returned as a dictionary wth the slot name
            If it is not, a similarity check is performed.
                If there is at least one value with similarity score > 0.7 in the CLASS_NAMES list,
                name with the highest similarity score is chosen and returned as a dictionary
                wth the slot name
                If there is not, None is returned.

        :param slot_value: Value of the entity class name
        :return: dictionary containing the slot name and its value
        """

        if slot_value not in CLASS_NAMES:
            similarity_perc = [Levenshtein.jaro(slot_value.lower(), s.lower()) for s in CLASS_NAMES]
            if max(similarity_perc) < 0.7:
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
        """
        A method to validate the input for entity class type.
        First it checks if the entity is present in the global variable CLASS_TYPES.
           If it is, it is returned as a dictionary wth the name of the slot
           If it is not, a similarity check is performed.
                If there is at least one value with similarity score > 0.7 in the CLASS_TYPES list,
                the class type with the highest similarity score is chosen and returned as a dictionary
                with the slot name
                If there is not, None is returned.

        :param class_type: Value of the entity class type
        :return: dictionary containing the slot name and its value
       """

        class_name = tracker.get_slot('class_name')
        if class_type in CLASS_TYPES_EN_DE.keys():
            class_type = CLASS_TYPES_EN_DE.get(class_type)
        elif class_type not in CLASS_TYPES:
            similarity_perc = [Levenshtein.jaro(class_type.lower(), s.lower()) for s in CLASS_TYPES]
            if max(similarity_perc) < 0.7:
                return {"class_type": None}
            else:
                most_similar_index = similarity_perc.index(max(similarity_perc))
                class_type = CLASS_TYPES[most_similar_index]
        df = perform_query(mode=MODE, looking_for='all_classes', class_name=class_name,
                           class_type=class_type, con=sqa_con)
        if df.empty:
            class_type_string = '' if class_type is None else CLASS_TYPES_DE_EN.get(class_type)
            dispatcher.utter_message(text=f"I'm sorry. There is no {class_type_string} {class_name} in the database.")
            return {"class_type": None}
        return {"class_type": class_type}


# validation of the class_name_form
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
        """
        A method to validate the input for entity class name.
        First it checks if the entity is present in the global variable CLASS_NAMES.
            If it is, it is returned as a dictionary wth the slot name
            If it is not, a similarity check is performed.
                If there is at least one value with similarity score > 0.7 in the CLASS_NAMES list,
                name with the highest similarity score is chosen and returned as a dictionary
                wth the slot name
                If there is not, None is returned.

        :param slot_value: Value of the entity class name
        :return: dictionary containing the slot name and its value
        """

        if slot_value not in CLASS_NAMES:
            similarity_perc = [Levenshtein.jaro(slot_value.lower(), s.lower()) for s in CLASS_NAMES]
            if max(similarity_perc) < 0.7:
                # dispatcher.utter_message(text=f"I don't recognize this class name. Could you try again please?")
                return {"class_name": None}
            else:
                most_similar_index = similarity_perc.index(max(similarity_perc))
                slot_value = CLASS_NAMES[most_similar_index]
                return {"class_name": slot_value}
        return {"class_name": slot_value}


# if the class type slot is not filled, ask for it
class AskForClassTypeAction(Action):
    def name(self) -> Text:
        return "action_ask_class_type"

    def run(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        """
        A method to as the user for the missing value for the slot class_type.
        If the class type is not mentioned in the user input, this method checks
        how many different class types are there in the database for the given class name.
        If there is only one class type, then it is automatically chosen.
        If there are more class types, then the user is presented with a choice of the available types

        :param tracker: Tracker to get the other slots from
        :return: list of SlotSet with the slot name and value
        """
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
            class_type = available_class_types[0]
            message = choose_action(tracker, class_name, class_type, weekday)
            dispatcher.utter_message(text=message)

            return [SlotSet('class_type', class_type)]
        return []


# Return answer
class ActionGetAnswer(Action):
    def name(self) -> Text:
        return "action_get_answer"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]):
        """
        A method that chooses the correct action to perform based on the given slots

        :param tracker: Tracker to get the other slots from
        """
        class_name = tracker.get_slot('class_name')
        class_type = tracker.get_slot('class_type')
        weekday = tracker.get_slot('weekday')
        message = choose_action(tracker, class_name, class_type, weekday)
        dispatcher.utter_message(text=message)

        return [SlotSet('class_name', None), SlotSet('class_type', None), SlotSet('weekday', None)]


def return_class_start_time(class_name, class_type, weekday) -> Text:
    """
    Method to return information about the starting time of a class if available in the DB.
    Otherwise, output a message informing that the requested information is not present in the DB

    :param class_name: slot containing the validated class name
    :param class_type: slot containing the validated class type
    :param weekday: slot containing the weekday

    :return: Answer to the user's question
    """
    message = ''
    weekday_string = ''
    if weekday is not None:
        weekday_string = ' on ' + weekday
        weekday = WEEKDAYS_EN_DE.get(weekday)
    df = perform_query(mode=MODE, looking_for='start_time', class_name=class_name,
                       class_type=class_type, weekday=weekday, con=sqa_con)
    if df.empty:
        class_type_string = '' if class_type is None else 'the ' + CLASS_TYPES_DE_EN.get(class_type)
        message = f"I'm sorry, there is no data about the starting time of {class_type_string} {class_name}"
        message += weekday_string
    else:
        # if weekday is not specified in the query, output information about the starting time on all days
        for i, row in df.iterrows():
            if row['week_day'] is not None:
                if i == 0:
                    message += f"The {CLASS_TYPES_DE_EN.get(class_type)} {class_name} starts at {row['start_time']} " \
                               f"on {WEEKDAYS_DE_EN.get(row['week_day'])}"
                else:
                    message += f" and at {row['start_time']} on {WEEKDAYS_DE_EN.get(row['week_day'])}"
    return message + '.'


def return_class_lecturer(class_name, class_type) -> Text:
    """
    Method to return information about the lecturer of a class if available in the DB.
    Otherwise, output a message informing that the requested information is not present in the DB

    :param class_name: slot containing the validated class name
    :param class_type: slot containing the validated class type

    :return: Answer to the user's question
    """
    df = perform_query(mode=MODE, looking_for='lecturer', class_name=class_name,
                       class_type=class_type, con=sqa_con)
    if df.empty or pd.isna(df.iloc[0]['lecturer']):
        class_type_string = '' if class_type is None else 'the ' + CLASS_TYPES_DE_EN.get(class_type)
        message = f"I'm sorry, there is no data about the lecturer of {class_type_string} {class_name}"
    else:
        message = f"The lecturer of the {CLASS_TYPES_DE_EN.get(class_type)} {class_name} is {df.iloc[0]['lecturer']}."
    return message


def return_class_location(class_name, class_type, weekday) -> Text:
    """
    Method to return information about the location of a class if available in the DB.
    Otherwise, output a message informing that the requested information is not present in the DB

    :param class_name: slot containing the validated class name
    :param class_type: slot containing the validated class type
    :param weekday: slot containing the weekday

    :return: Answer to the user's question
    """
    weekday_string = ''
    if weekday is not None:
        weekday_string = ' on ' + weekday
        weekday = WEEKDAYS_EN_DE.get(weekday)
    df = perform_query(mode=MODE, looking_for='location', class_name=class_name,
                       class_type=class_type, weekday=weekday, con=sqa_con)
    if df.empty:
        class_type_string = '' if class_type is None else 'the ' + CLASS_TYPES_DE_EN.get(class_type)
        message = f"I'm sorry, there is no data about the location of {class_type_string} {class_name}"
        message += weekday_string
    else:
        if weekday_string == '' and df.iloc[0]['week_day'] is not None:
            weekday_string = ' on ' + WEEKDAYS_DE_EN.get(df.iloc[0]['week_day'])
        message = f"The {CLASS_TYPES_DE_EN.get(class_type)} {class_name} {weekday_string} takes place " \
                  f"in {df.iloc[0]['room']} {df.iloc[0]['floor'].strip()}, " \
                  f"{df.iloc[0]['building']}, {df.iloc[0]['facility']}. The address is {df.iloc[0]['address'].strip()}."
    return message


def return_open_question(class_name, tracker) -> Text:
    """
    Method to return information about an open question for a class if available in the DB.
    Otherwise, output a message informing that the requested information is not present in the DB

    :param class_name: slot containing the validated class name
    :param tracker: Tracker to get the other slots from

    :return: Answer to the user's question
    """
    df = perform_query(mode=MODE, looking_for='open_question', class_name=class_name, con=sqa_con)
    if df.empty or pd.isna(df.iloc[0]['txt']):
        message = f"I'm sorry, there is no data on this topic about {class_name} in the database."
    else:
        # clean HTML syntax
        context = strip_tags(df.iloc[0]['txt'])
        question = tracker.latest_message['text']
        # answer the user's question based on the comment field about the class
        # in the DB using the ELECTRA model
        message = qa(question, context, electra_model, electra_tokenizer)
    return message


def return_class_moodle_link(class_name, class_type, weekday) -> Text:
    """
    Method to return information about the Moodle link for a class if available in the DB.
    Otherwise, output a message informing that the requested information is not present in the DB

    :param class_name: slot containing the validated class name
    :param class_type: slot containing the validated class type
    :param weekday: slot containing the weekday

    :return: Answer to the user's question
    """
    weekday_string = ''
    if weekday is not None:
        weekday_string = ' on ' + weekday
        weekday = WEEKDAYS_EN_DE.get(weekday)
    df = perform_query(mode=MODE, looking_for='moodle_link', class_name=class_name,
                       class_type=class_type, weekday=weekday, con=sqa_con)
    if df.empty or pd.isna(df.iloc[0]['hyperlink']):
        class_type_string = '' if class_type is None else 'the ' + CLASS_TYPES_DE_EN.get(class_type)
        message = f"I'm sorry, there is no data about the moodle link of {class_type_string} {class_name}"
        message += weekday_string
    else:
        message = f"The moodle link for the {CLASS_TYPES_DE_EN.get(class_type)} {class_name} {weekday_string} is {df.iloc[0]['hyperlink']}."
    return message


def choose_action(tracker, class_name, class_type, weekday):
    """
    Method to trigger the appropriate action based on the intent.
    Pass the available slots to the chosen action

    :param tracker: Tracker to get the other slots from
    :param class_name: name of the class if present
    :param class_type: type of the class if present
    :param weekday: weekday if present
    :return: Answer to the user's question
    """
    reversed_events = list(reversed(tracker.events))
    intent_name = ''
    message = ''

    # iterate through the reversed events in the tracker until an intent
    # different from 'inform' is found
    for event in reversed_events:
        if 'parse_data' in event.keys():
            intent_name = event['parse_data']['intent']['name']
            if intent_name != 'inform':
                break
    if intent_name == 'ask_class_start_time':
        message = return_class_start_time(class_name, class_type, weekday)
    elif intent_name == 'ask_class_lecturer':
        message = return_class_lecturer(class_name, class_type)
    elif intent_name == 'ask_class_location':
        message = return_class_location(class_name, class_type, weekday)
    elif intent_name == 'ask_class_moodle_link':
        message = return_class_moodle_link(class_name, class_type, weekday)
    elif intent_name == 'ask_open_question':
        message = return_open_question(class_name, tracker)
    return message


def qa(question, answer_text, model, tokenizer):
    """
    Method to get an answer from context

    :param question: question that needs to be answered
    :param answer_text: context, from which the answer should be extracted
    :param model: specify model
    :param tokenizer: specify tokenizer

    :return: model's answer for the user question
    """
    inputs = tokenizer.encode_plus(question, answer_text, add_special_tokens=True, return_tensors="pt")
    input_ids = inputs["input_ids"].tolist()[0]

    outputs = model(**inputs)
    answer_start_scores = outputs.start_logits
    answer_end_scores = outputs.end_logits

    # get the most likely beginning of answer with the argmax of the score
    answer_start = torch.argmax(
        answer_start_scores
    )
    # get the most likely end of answer with the argmax of the score
    answer_end = torch.argmax(answer_end_scores) + 1

    answer = tokenizer.convert_tokens_to_string(tokenizer.convert_ids_to_tokens(input_ids[answer_start:answer_end]))
    answer = answer.replace("#", "")

    return answer
