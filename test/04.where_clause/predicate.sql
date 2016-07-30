select * from a
where c1=c2 and c2=c2 or c3=c3
and t1.c1=t2.c2 or t1.c2=t2.c2
and t1.c1 between 1 and 100
and t1.c1 like '%dkfd%'
and t1.c1 like 'akdf%' escape '%'
and t1.c1 is null
and t1.c1 is not null
and t1.c1 in (1,2,3)
and t1.c1 in ('a','b','c')
and exists (select 1 from a where c1=1 or c1=2)