get_available_class_types_by_class_name_query = '''
select distinct class_type
from class_info_view civ 
where class_name = '%s'
'''


get_all_classes_info_query = 'select * from class_info_view'

get_class_start_time_query = '''
select class_name, class_type, start_time, week_day
from class_info_view civ 
where class_name = '%s'
and class_type = '%s'
'''

get_lecturer_query = '''
select lecturer
from class_info_view civ 
where class_name = '%s'
and class_type = '%s'
'''