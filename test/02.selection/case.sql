select case a when '1' then a1 else a9 end
,case b when '1' then b1 when '2' then b2 when '3' then b3 else b9 end
,case when 1=1 then a1 when a=b then a2 else a9 end
from tbl