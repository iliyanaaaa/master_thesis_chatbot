## Import the CSVSQL
from csvkit.utilities.csvsql import CSVSQL

# Define Args for Query 1 and 2
# args_query1 = ['--query', 'select distinct class_name from class_info_view', 'class_info_view.csv']
args_query2 = ['--query', 'select count(class_name)  from class_info_view', 'data/csv_exports/class_info_view.csv']

# # Excute and print results of Query1
# print("Result for the query - 1:")
# result1 = CSVSQL(args_query1)
# print(result1.main())

# Excute and print results of Query2
print("Result for the query - 2:")
result2 = CSVSQL(args_query2)
print(result2.main())
