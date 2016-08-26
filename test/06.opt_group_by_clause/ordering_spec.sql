select 1 from a
where c1=1
group by c1,c2 asc,c3 desc,4,5,c1+c2,(select a from d where c1=c2)
order by c1,c2 asc,c3 desc,4,5,c1+c2,(select a from d)
