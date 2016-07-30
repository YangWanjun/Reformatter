SELECT NULLIF(COALESCE(current_year,previous_year), 0)
,nullif(coalesce(case a when 1 then a1 when 2 then a2 else a9 end), 'abc') as exp1
,nullif(0, coalesce(case a when 1 then a1 when 2 then a2 else a9 end)) as exp1
,nullif(coalesce(case a when 1 then a1 when 2 then a2 else a9 end), coalesce(case a when 1 then a1 when 2 then a2 else a9 end)) as exp1
FROM budgets