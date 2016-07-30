select *
from tbl as t1 join t2 on t1.c1 = t2.c2
left join t3 on  t3.c1 = t2.c1
right join t4 on t4.c1 = t1.c1
inner join table5 t5 on t5.c1=t1.c1 and t5.c2 =t6.c2
left outer join table6 as t6 on t6.c1=t1.c1 or t6.c2 =t1.c2
left outer join (select * from tt7, tt8 as t8) as t7 on t6.c1=t1.c1 or t6.c2 =t1.c2
left join (select distinct 1 from tt9 left join tt10 on tt9.c1 = tt10.c1) as t9 on t9.c1=t1.c1 and t9.c2=t1.c2