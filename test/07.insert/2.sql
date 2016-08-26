insert into a(a,b,c,d,e) values(1,convert(varchar(20), c1.date1)
,cast(1 as char),
(select c4 from c where c1=1),5)