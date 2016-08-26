update table1 set c1=1,c2=2,c3=3
,c4=(select max(sub_c1) from sub_table1)
where c1=1