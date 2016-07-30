select coalesce(a,b,'a b c,', 2)
,coalesce(case a when 1 then a1 when 2 then a2 else a9 end, cast(1 as varchar(10)), convert(char(15), 1234343)) as exp1
,coalesce(case a when 1 then a1 when 2 then a2 else a9 end) as exp2