## Import the CSVSQL
import Levenshtein
import pandas as pd
from csvkit.utilities.csvsql import CSVSQL

# Define Args for Query 1 and 2
# args_query1 = ['--query', 'select distinct class_name from class_info_view', 'class_info_view.csv']
from actions.db_connections import SQA_CONN_PUB
from actions.sql_queries import get_class_is_about, get_weekday_en_de, add_class_type_query, add_weekday_query, \
    class_info_view_txt_query_class_name, get_class_types_query

args_query2 = ['--query', 'select count(class_name)  from class_info_view', 'data/csv_exports/class_info_view.csv']
args_query3 = ['--query', get_weekday_en_de, 'data/csv_exports/weekdays.csv']

# # Excute and print results of Query1
# print("Result for the query - 1:")
# result1 = CSVSQL(args_query1)
# print(result1.main())

# Excute and print results of Query2
# print("Result for the query - 2:")
# result2 = CSVSQL(args_query3)
# print(result2.main().__class__)
# df = pd.DataFrame(result2.main())
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
            df = pd.read_csv('/data/csv_exports/weekdays.csv')
        elif looking_for == 'types_of_classes':
            df = pd.read_csv('/data/csv_exports/types_of_classes.csv')
        else:
            df = pd.read_csv('/data/csv_exports/class_info_view_txt.csv')
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


# df = pd.read_csv('C:/Users/tarpo/PycharmProjects/master_thesis_chatbot/data/csv_exports/class_info_view_txt.csv')
# variables = ['class_name','class_type']
#
# df = df[variables].drop_duplicates(inplace=True)
#
# print(df.columns)
# print(df['class_name'].values)

df = perform_query(mode='database', looking_for='moodle_link', class_name='Social Hydrology',
                   class_type=None, weekday=None, con=SQA_CONN_PUB)

if pd.isna(df.iloc[0]['hyperlink']):
    print('is nan')

