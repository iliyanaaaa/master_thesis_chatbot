get_class_start_time = f'''
                        select b
                        from public.test_table tt 
                        where a = '%s'
                        and class_type = '%s'
                        '''