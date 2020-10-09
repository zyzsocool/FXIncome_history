import datetime
import fxincome
# code1='190210'
# ctype1='附息'
# initial_date1=datetime.datetime(2019,5,21)
# end_date1=datetime.datetime(2029,5,21)
# coupon_rate1=3.65/100
# frequency1=1
# quantity=100
# assessment_date=datetime.datetime(2028,5,20)
# curve = {
#     '0': 0.009068,
#     '3M': 0.009601,
#     '6M': 0.010829,
#     '9M': 0.012166,
#     '1Y': 0.012194,
#     '2Y': 0.015199,
#     '3Y': 0.016117,
#     '4Y': 0.018023,
#     '5Y': 0.020187,
#     '10Y': 0.026698,
#     '20Y': 0.032858,
#     '30Y': 0.034564}


code1='209901'
ctype1='贴现'
initial_date1=datetime.datetime(2020, 1, 6)
end_date1=datetime.datetime(2020, 4, 6)
coupon_rate1=0.018911
frequency1=0
face_value=100
assessment_date=datetime.datetime(2020,3,1)
curve = {
    '0': 0.009068,
    '3M': 0.009601,
    '6M': 0.010829,
    '9M': 0.012166,
    '1Y': 0.012194,
    '2Y': 0.015199,
    '3Y': 0.016117,
    '4Y': 0.018023,
    '5Y': 0.020187,
    '10Y': 0.026698,
    '20Y': 0.032858,
    '30Y': 0.034564}




bond1=fxincome.Bond(code1, ctype1, initial_date1, end_date1, coupon_rate1, frequency1)
position1=fxincome.PositionBond(bond1, face_value, assessment_date, curve)

print(position1.asset.ytm(assessment_date, curve))
print(position1.cleanprice)
print(position1.realdailyR())
print(position1._realdailyR_history())
position1.change(newdate=datetime.datetime(2020,4,6))
#print(position1.cleanprice_interestgain())
print(position1.cleanprice_interestgain())


# code1='160018'
# ctype1='附息'
# initial_date1=datetime.datetime(2016,8,4)
# end_date1=datetime.datetime(2017,8,4)
# coupon_rate1=2.14/100
# frequency1=1
#
# bond1=fxincome.Bond(code1, ctype1, initial_date1, end_date1, coupon_rate1, frequency1)
#
#
# quantity=100
# assessment_date=datetime.datetime(2017,6,20)
# curve = {
#     '0': 0.009068,
#     '3M': 0.009601,
#     '6M': 0.010829,
#     '9M': 0.012166,
#     '1Y': 0.012194,
#     '2Y': 0.015199,
#     '3Y': 0.016117,
#     '4Y': 0.018023,
#     '5Y': 0.020187,
#     '10Y': 0.026698,
#     '20Y': 0.032858,
#     '30Y': 0.034564}
#
# position1=fxincome.PositionBond(bond1, quantity, assessment_date, curve)
# position1.cleanprice=99.9
# print(position1.cashflow())
# print(position1.realdailyR())
# print(position1._realdailyR_history())