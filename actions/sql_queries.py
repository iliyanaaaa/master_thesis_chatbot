get_available_class_types_by_class_name_query = '''
select distinct class_type
from class_info_view civ 
where class_name = '%s'
'''


get_all_classes_info_query = 'select * from class_info_view'

get_types_of_classes = 'select * from types_of_classes'

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

get_location_query = '''
select room, floor , building , facility , address 
from class_info_view civ 
where class_name = '%s'
and class_type = '%s'
'''

get_moodle_link_query = '''
select hyperlink
from class_info_view civ 
where class_name = '%s'
and class_type = '%s'
'''

get_class_is_about = '''
select txt
from class_info_view_txt civt 
where class_name = '%s'
'''

class_info_view_txt_query_class_name = '''
select distinct %s
from class_info_view_txt civt 
where class_name = '%s'
'''

add_weekday_query = "and week_day = '%s'"
add_class_type_query = "and class_type = '%s'"

get_class_types_query = '''select abbr, class_type_de
                            from (
                            select max(length(abbr)), abbr, class_type_de
                            from types_of_classes toc 
                            group by abbr, class_type_de) as t
                            order by max'''

get_weekday_en_de_complex = '''
with te as (
select *
from texte t 
join r_texte rt 
on rt.texteid = t.texteid 
where rt.tabelle = 'k_wochentag')
select txt as weekday_en, ltxt as weekday_de
from te
join k_wochentag kw 
on kw.wochentagid = te.tabpk
where te.spalte = 'ltxt'
'''

get_weekday_en_de = '''
select * from weekdays
'''

get_ueberschrift_en_de = '''
with te as (
select *
from texte t 
join r_texte rt 
on rt.texteid = t.texteid 
where rt.tabelle = 'ueberschrift')
select te.txt, ue.txt
from te
join ueberschrift ue
on ue.ueid = te.tabpk'''

get_veranstaltung_en_de = '''
with te as (
select *
from texte t 
join r_texte rt 
on rt.texteid = t.texteid 
where rt.tabelle = 'veranstaltung')
select txt, dtxt
from te
join veranstaltung v
on v.veranstid  = te.tabpk
'''

get_einrichtung_en_de = '''
with te as (
select *
from texte t 
join r_texte rt 
on rt.texteid = t.texteid 
where rt.tabelle = 'einrichtung')
select txt, dtxt
from te
join einrichtung e
on e.eid  = te.tabpk
where te.spalte = 'dtxt' '''

get_rhythmus_en_de = '''
with te as (
select *
from texte t 
join r_texte rt 
on rt.texteid = t.texteid 
where rt.tabelle = 'k_rhythmus')
select txt, dtxt
from te
join k_rhythmus kr
on kr.rhythmusid  = te.tabpk
where te.spalte = 'dtxt' '''

get_class_is_about_complex = '''
select distinct txt, class_type from (
with blo as (
select *
from blobs b
join r_blob rb
on rb.blobid  = b.blobid 
where rb.tabelle = 'veranstaltung')
select distinct  blo.txt, v.dtxt, blo.spalte
from blo
join veranstaltung v
on v.veranstid = blo.tabpk) as x
join class_info_view civ 
on x.dtxt = civ.class_name 
where spalte = 'kommentar' and txt is not null and class_name like '%%{class_name}%%'
'''
