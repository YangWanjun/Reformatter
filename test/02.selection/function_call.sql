select func1(a),func2(a,b),func3(1,3,4)
,scope.func4(1,2,3,4),scope1.scope2.func5('abc'),scope1.scope2.scope3.func5('abc')
,scope..func1('2015'),scope..scope1.func2(1), left('abcdefg'), right('abc')
,current_date,current_time,current_timestamp
from t