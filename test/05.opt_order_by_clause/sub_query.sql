select 1 from(
select c1 from a
where c1=1
and c2 = (select max(c2) from a where c2=c2 order by c2,c3)
and (select avg(c2) from a where c2=c2 order by c2,c3) = c3
and min(c2) = (select max(c2) from a where c2=c2 order by c2,c3)
order by c1,c2 asc,c3 desc,4,5) t1 order by 1