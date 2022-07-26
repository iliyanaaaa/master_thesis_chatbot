get_class_start_time = '''
                        select b
                        from public.test_table tt 
                        where a = '%s'
                        and class_type = '%s'
                        '''

get_available_class_types_by_class_name = "Select class_type from test_table where a = '%s'"
