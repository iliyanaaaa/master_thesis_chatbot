-- create view with all class information

create view class_info
as select v.dtxt as class_name, kva.dtxt as class_type, hyperlink, freigabe, vt.belegpflicht, ks.dtxt as lang,
 begindat as start_date, endedat as end_date, v.teilnehmermax as max_part, beginn as start_time, ende as end_time, kw.dtxt as week_day, kr.dtxt as rhythm,
 kr.dtxt as parallel,  p.vorname || ' ' || p.nachname as lecturer, r.dtxt || ' ' || r.ktxt as room, geschossnummer as "floor",
 hu_tuning_kontakt_strasse as address, kg.dtxt as building, e.dtxt as facility
from veranstaltung v
join k_verart kva
on kva.verartid = v.verartid
join veransttermin vt
on v.veranstid = vt.veranstid
join r_veranstpers rvp
on rvp.vtid = vt.vtid
join personal p
on p.pid = rvp.pid
join k_sprache ks
on v.unterrsprache = ks.spracheid
join k_wochentag kw
on vt.wochentagid = kw.wochentagid
join k_rhythmus kr
on kr.rhythmusid = vt.rhythmusid
join k_parallel kp
on kp.parallelid = vt.parallelid
join raum r
on r.rgid = vt.rgid
join k_gebaeude kg
on kg.gebid = r.gebid
join einrichtung e
on e.eid = r.eid

-- create table for the class type abbreviations

-- public.types_of_classes definition

-- Drop table

-- DROP TABLE public.types_of_classes;

CREATE TABLE public.types_of_classes (
	abbr varchar(20) NULL,
	class_type varchar(20) NULL
);
INSERT INTO public.types_of_classes (abbr,class_type) VALUES
	 ('l','Vorlesung'),
	 ('lecture','Vorlesung'),
	 ('lect','Vorlesung'),
	 ('vl','Vorlesung'),
	 ('vorlesung','Vorlesung'),
	 ('exercise','Übung'),
	 ('üb','Übung'),
	 ('ü','Übung'),
	 ('seminar','Seminar'),
	 ('s','Seminar');
INSERT INTO public.types_of_classes (abbr,class_type) VALUES
	 ('sem','Seminar'),
	 ('e','Übung'),
	 ('ex','Übung');
