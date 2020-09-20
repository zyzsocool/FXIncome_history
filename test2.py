#对程序所有的函数都测试一遍
import fxincome
import datetime
#1初始定义
#1.1定义asset
#1.1.1定义asset的信息准备
#1.1.1.1第一只债券的信息准备
code1='190210'
ctype1='附息'
initial_date1=datetime.datetime.strptime('20190521', '%Y%m%d')
end_date1=datetime.datetime.strptime('20290521', '%Y%m%d')
coupon_rate1=3.65/100
frequency1=1
#1.1.1.2第二只债券的信息准备
code2='190015'
ctype2='附息'
initial_date2=datetime.datetime.strptime('20191121', '%Y%m%d')
end_date2=datetime.datetime.strptime('20291121', '%Y%m%d')
coupon_rate2=3.13/100
frequency2=1



#1.1.2定义asset
bond1=fxincome.Bond(code1, ctype1, initial_date1, end_date1, coupon_rate1, frequency1)
bond2=fxincome.Bond(code2, ctype2, initial_date2, end_date2, coupon_rate2, frequency2)
#1.2定义position
#1.2.1定义position的信息准备
face_value=100
assessment_date=datetime.datetime.strptime('20200821', '%Y%m%d')
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
#1.2.2定义position及positisonlist
position1=fxincome.PositionBond(bond1, face_value, assessment_date, curve)
position2=fxincome.PositionBond(bond2, face_value, assessment_date, curve)
positionlist=[position1,position2]
#1.3定义hdp
#1.3.1定义hdp的信息准备
#1.3.1.1初始hdp信息准备
date0 = datetime.datetime.strptime('20200821', '%Y%m%d')
curve_mu0 = {
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
curve_flc0 = {
    '0': 0.001,
    '3M': 0.001,
    '6M': 0.001,
    '9M': 0.001,
    '1Y': 0.001,
    '2Y': 0.001,
    '3Y': 0.001,
    '4Y': 0.001,
    '5Y': 0.001,
    '10Y': 0.001,
    '20Y': 0.001,
    '30Y': 0.001}
buysell0 = {}
#1.3.1.2期间第一个hdp信息准备
date1 = datetime.datetime.strptime('20200921', '%Y%m%d')
curve_mu1 = {
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
curve_flc1 = {
    '0': 0.001,
    '3M': 0.001,
    '6M': 0.001,
    '9M': 0.001,
    '1Y': 0.001,
    '2Y': 0.001,
    '3Y': 0.001,
    '4Y': 0.001,
    '5Y': 0.001,
    '10Y': 0.001,
    '20Y': 0.001,
    '30Y': 0.001}
buysell1 = {'190210':100}
#1.3.1.3期间第二个hdp信息准备
date2 = datetime.datetime.strptime('20201021', '%Y%m%d')
curve_mu2 = {
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
curve_flc2 = {
    '0': 0.001,
    '3M': 0.001,
    '6M': 0.001,
    '9M': 0.001,
    '1Y': 0.001,
    '2Y': 0.001,
    '3Y': 0.001,
    '4Y': 0.001,
    '5Y': 0.001,
    '10Y': 0.001,
    '20Y': 0.001,
    '30Y': 0.001}
buysell2 = {'190210':-150}
#1.3.1.4结束hdp信息准备
date00 = datetime.datetime.strptime('20201221', '%Y%m%d')
curve_mu00 = {
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
curve_flc00 = {
    '0': 0.001,
    '3M': 0.001,
    '6M': 0.001,
    '9M': 0.001,
    '1Y': 0.001,
    '2Y': 0.001,
    '3Y': 0.001,
    '4Y': 0.001,
    '5Y': 0.001,
    '10Y': 0.001,
    '20Y': 0.001,
    '30Y': 0.001}
buysell00 = {}

#1.3.2定义hdp和hdplist

hdp_0 = fxincome.Hdp(date0, curve_mu0, buysell0, curve_flc0)
hdp_1 = fxincome.Hdp(date1, curve_mu1, buysell1, curve_flc1)
hdp_2 = fxincome.Hdp(date2, curve_mu2, buysell2, curve_flc2)
hdp_00 = fxincome.Hdp(date00, curve_mu00, buysell00, curve_flc00)
hdplist=[hdp_0,hdp_1,hdp_2,hdp_00]
#1.4定义porfolio
myportfolio=fxincome.Portfolio(positionlist, hdplist)


#2函数测试
#2.1asset的函数测试
print('asset的函数测试')
print('ytm:',bond1.ytm(assessment_date,curve))
print('cashflow:',bond1.cashflow(assessment_date))
print('pv:',bond1.pv(assessment_date,curve))
print('cleanprice:',bond1.cleanprice_func(assessment_date,curve))
print('dv01:',bond1.dv01(assessment_date,curve))

#2.2position的函数测试
print('position的函数测试')
print('cashflow:',position1.cashflow())
print('pv:',position1.pv())
print('cleanprice:',position1.cleanprice)
print('dv01:',position1.dv01())
print('realR:',position1.realR)
print('interestgain:',position1.cleanprice_interestgain())






#2.3portfolio测试
myportfolio.bsforcast_tpl()
myportfolio.bsforcast_tpl_plot()
myportfolio.bsforcast_oci()
myportfolio.bsforcast_oci_plot(1)