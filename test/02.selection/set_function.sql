select count(*) 
,count(distinct c1)
,sum(c1)
,sum(all c1)
,avg(c1)
,avg(distinct c1)
,min(c1)
,min(all c1)
,max(c1)
,max(distinct c1)
from table1