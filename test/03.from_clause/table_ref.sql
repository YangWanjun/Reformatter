select 1
from tbl as t1, tbl2 t2
,(select a from b) as t3
,(select a from b as b1, a ) t4