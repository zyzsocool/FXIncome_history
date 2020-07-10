# FXIncome（2.1）

当前版本主要是三个模块：（历史版本由于没有考虑模块化的结构，已经放弃）

### 0.版本更新
#### 2.1版本更新
* 2.0版本中bpforcast_tpl中如果assementdate为付息日，会在现金头寸和债券头寸里重复计算当天的现金流，新版本进行了改正。
* bpforcast的输出结果最后增加了核算区间中每一次发生现金流变动的日子的累计现金流，以便于进行现金头寸管理。同时在最后输出每一个债券的剩余面值。
* 增加了bpforcast_oci函数
* 为配套bpforcast_oci函数，asset_bond类增加了属性与方法

#### 可能需要修改问题
* 计算净价和全价时保留了过多的小数，系统一般是保留4位的，如103.1245，现在会保留到很多位，如103.12451234832,会有一点误差，但是影响不大

### 1.asset模块：

定义asset父类，下面分子类asset_bond,asset_irs等。对单笔资产进行处理，债券方面包括算现金流，算pv以及dv01，irs方面暂时未写，其他资产未来可拓展。

#### asset父类

```python
class asset():
    def __init__（self，……）
        self.code=code
        self.ctype=ctype
        self.initialdate=initialdate
        self.enddate=enddate
        self.facevalue=facevalue
        self.couponrate=couponrate
        self.assementdate=assementdate
        self.curve=curve
    def cashflow(self):
    def pv(self):
    def dv01(self):
    def change(self）：
```

##### 输入

* code 资产的代码，债券用债券代码，irs用交易单号
* ctype 资产的类型，债券现在分为附息，贴现和到期还本付息，irs以后应该要分fr007，lpr和shibor（要不要分成fr007s1y，fr007s5y这么细分后面具体再写）
* initialdate 资产的起息日，datetime格式
* enddate 资产的到期日，datetime格式
* facevalue 资产的面值，债券是本金，irs是名义本金
* couponrate 资产的票面利率，irs的是固定端利息
* assementdate 核算日，datetime格式
* curve 该资产对应的收益率曲线，dic格式，key是期限（3M，1Y类型的），value是收益率

##### 输出

asset的共有函数其实只有change是适合所有子类的，用来改变资产的收益率曲线、核算日和面值。其他函数具体到子类分析。

#### asset_bond(asset)

```python
class asset_bond(asset):
    def __init__(self,……)
        super().__init__()
        self.frequency=frequency
        self.cleanprice=cleanprice
        self.realR=None
        self.initial_assementdate=assementdate
    def ytm(self):
    def cashflow(self):
    def pv(self):
    def dv01(self):
    def cleanprice_fuc(self):
    def cleanprice_fill(self)
    def realdailyR(self):
    def cleanprice_interestgain(self)
    
```



##### 输入

* 大部分继承父类
* frequency 付息债券一年付息次数，其他类型债券用不上，统一填0
* cleanprice债券净价，主要是oci核算的时候要用到
* realR真实日利率，主要是oci核算的时候要用到，不用自己输的，后面有个函数专门算
* initial_assementdate最初的核算日，主要是oci核算时要用到

##### 输出

* change继承父类
* ytm输出根据收益率曲线计算的债券的收益率
* cashflow输出一个dic，每个key是datetime格式的日期，value是float格式的现金流
* pv输出一个两个元素的list，第一个元素是pv，第二个元素是一个dic，是将cashflow的现金流折现到assetmentdate。即第二个元素所有value的加和就是pv
* dv01输出债券的dv01
* cleanprice_fuc计算债券的净价
* cleanprice_fill将净价补充到资产的属性中
* realdailyR计算oci核算中的真实日利率（由于这里用了插值法，进行了较多的循环，所以这是程序跑得慢的主要原因）
* cleanprice_interestgain得出assementdate的折溢摊净价，以及initial_assementdate到assementdate的利息收入

#### asset_irs(asset)

暂时没写，未来要进行拓展



### 2.profolio模块：

对资产组合进行处理，当前主要是进行buysell测试，而且是基于tpl核算下的损益计算。后期会拓展基于oci核算下的测试、资产组合压力测试以及irs与债券组合的综合模式等。

#### hdp类



```python
class hdp():
    def __init__(self,……)
        self.date=date
        self.curve_mu=curve_mu
        self.buysell=buysell
        self.curve_flc=curve_flc
     def curvemo(self)
    
```

hdp类用来记录每一次交易操作的具体信息，每一个hdp代表某一天的所有操作

##### 输入

* date是进行操作的日期，datetime格式
* curve_mu是操作日的收益率曲线，dic格式，key是期限（3M，1Y类型的），value是收益率
* buysell是关于交易操作的dic，每个key是操作资产的code，每个value是操作的facevalue，正代表买入，负代表卖出
* curve_flc是利率曲线95%概率的波动范围，key与curve_mu的一一对应，value是波动范围

##### 输出

* curvemo输出一个随机收益率曲线，均值与波动范围由输入的curve_mu和curve_flc决定，是一个dic，格式与curve_mu一样



#### profolio类



```python
class profolio():
    def __init__(self,assetlist,hdplist):
        self.asset_initial=copy.deepcopy(asset)
        self.asset_deal=copy.deepcopy(asset)
        self.asset_notdeal=copy.deepcopy(asset)
        self.hdp=hdp
    def bsforcast_tpl(self):
    def bsforcast_oci(self):
    def bsforcast_plot(self):
    def stresstest(self):
```



profolio是这个程序的重点部分，可以对资产组合进行buy&sell测试以及压力测试等，后期也会拓展新的功能

##### 输入

* assetlist是一个以asset类为元素的list，[asset_1,asset_2,……，asset_n]
* hdplist是一个以hdp类为元素的list，hdplist=[hdp_1,hdp_2,……,hdp_n]

##### 输出

* bsforcast_tpl输出一个list，每个元素是一个dic，每个dic的元素为：

```
{
'hdp.date':               #操作日
'pv_begin':               #起始日的资产总值
----------------------操作情况下-----------------------  
'cashflow_his_deal':      #起始日到操作日的历史现金流（已实现）
                           datetime格式
'cash_end_deal':          #操作日的现金头寸，历史现金流加和
'cashflow_for_deal':      #操作日的未来折现现金流（未实现）
                           datetime格式
'pv_end_deal':            #操作日的债券头寸，折现现金流加和
-----------------------没操作情况下-------------------
'cashflow_his_notdeal':   #起始日到操作日的历史现金流（已实现）
                           datetime格式
'cash_end_notdeal':       #操作日的现金头寸，历史现金流加和
'cashflow_for_notdeal':   #操作日的未来折现现金流（未实现）
                           datetime格式
'pv_end_notdeal':         #操作日的债券头寸，折现现金流加和
}
```



所以每一个dic代表是起始日到某个操作日的各种信息，如当日的历史现金流、未来现金流、现金头寸、债券头寸等（包括操作情况下和不操作情况下），持有收益其实等于***现金头寸+债券头寸-起始日资产总值***，不想这个dic的信息过于臃肿，所以没有算出来。

这种模式是***基于tpl会计核算模式的结果***，也就是始终按市价计算的收益结果，也就是所有的收益都是假设将当前的所有资产按市场价格卖出所获得的收益。

* bsforcast_oci

bsforcast_oci是***基于oci会计核算模式的结果***，下一个版本主要补充的地方（代码已经写完了，但是说明还懒得写hhhh）

* bsforcast_tpl输出一个图，是进行多次模特卡罗模拟得出的收益图

* stresstest

进行压力测试，irs的压力测试在之前的模块中，后面要整合过来

### 3.assetput模块：

定义多个function，将资产和收益率信息从外部导入，预计主要是excel或者sql，为了其他使用者方便，可能会加入读取dataframe结构的函数

assetput要做到的作用是一次将所有资产和操作输入并快速输入到profolio中，并进行实验，做到不用浪费时间在数据输入上。

##### assetput

以assetput_excel为例：输入excel的地址exceladdress，输出一个assetlist，里面包括所有要处理的资产

```python
def assetput_excel(exceladdress)
    '…………'
    
    assetlist=[asset_1,asset_2,……，asset_n]
    #asset_i是一个asset类，在asset模块定义
    return assetlist
```

##### hdpput

以hdpput_excel为例：输入excel的地址exceladdress，输出一个hdplist，里面包括每次操作的信息。

```python
def hdpput_excel(exceladdress)
    '…………'
    hdplist=[hdp_1,hdp_2,……,hdp_n]
    #hdp_i是一个hdp类，在profolio模块定义
    return hdplist
```

### 4.代码使用案例

#### 从excel录入使用案例

```python
import FXIncome
exceladdress='C:\\Users\\zyzse\\Desktop\\模板.xlsx'

[assetlist,hdplist]=FXIncome.reading_excel(exceladdress)#读取excel信息并获得assetlist和hdplist
myprofilo=FXIncome.Profolio(assetlist,hdplist)#形成一个Profolio


#1.tpl算法
myprofilo.bsforcast_tpl()
#2.tpl蒙特卡洛算法（画图，不输入数字就默认模拟1000次）
myprofilo.bsforcast_tpl_plot()
#3.oci算法
myprofilo.bsforcast_oci()
#4.oci蒙特卡洛算法（画图，要算很久，不输入数字就默认模拟1000次）
myprofilo.bsforcast_oci_plot(100)
```



#### 原始bpforcast_tpl使用案例

这个案例很长很臃肿，实际上主要在信息输入部分，这个后面通过assetpu模块的完善可以一步处理。

```python
#1输入资产信息（当前只支持债券）
#1.1输入第一只债券190215
code='190215'
ctype='附息'
initialdate=datetime.datetime.strptime('20190920','%Y%m%d')
enddate=datetime.datetime.strptime('20290920','%Y%m%d')
facevalue=100
couponrate=0.0345
assementdate=datetime.datetime.strptime('20200421','%Y%m%d')
facevalue=100
curve={'0':0.004747,'3M':0.009423,'6M':0.010547,'9M':0.011818,'1Y':0.012109,'2Y':0.016011,'3Y':0.017809,'4Y':0.021618,'5Y':0.022202,'10Y':0.028510}
frequency=1
asset_1=FXIncome.asset_bond(code, ctype, initialdate, enddate, facevalue, couponrate, assementdate, curve, frequency)
print(asset_1.ytm())
print(asset_1.cashflow())
print(asset_1.pv())
print(asset_1.dv01())
#1.2输入第二只债券200203
code='200203'
ctype='附息'
initialdate=datetime.datetime.strptime('20200110','%Y%m%d')
enddate=datetime.datetime.strptime('20250110','%Y%m%d')
facevalue=100
couponrate=0.0323
assementdate=datetime.datetime.strptime('20200421','%Y%m%d')
facevalue=100
curve={'0':0.004747,'3M':0.009423,'6M':0.010547,'9M':0.011818,'1Y':0.012109,'2Y':0.016011,'3Y':0.017809,'4Y':0.021618,'5Y':0.022202,'10Y':0.028510}
frequency=1
asset_2=FXIncome.asset_bond(code, ctype, initialdate, enddate, facevalue, couponrate, assementdate, curve, frequency)
print(asset_2.ytm())
print(asset_2.cashflow())
print(asset_2.pv())
print(asset_2.dv01())

#1.3将所有资产放到list里
assetlist=[asset_1, asset_2]

#2输入操作信息
#2.1输入第一次操作信息，操作日为20200422
date=datetime.datetime.strptime('20200422','%Y%m%d')
curve_mu={'0':0.004747,'3M':0.009423,'6M':0.010547,'9M':0.011818,'1Y':0.012109,'2Y':0.016011,'3Y':0.017809,'4Y':0.021618,'5Y':0.022202,'10Y':0.028510}
curve_flc={'0':0,'3M':0,'6M':0,'9M':0,'1Y':0,'2Y':0,'3Y':0,'4Y':0,'5Y':0,'10Y':0}
buysell={'190215':-100,'200203':-100}
hdp_begin=FXIncome.hdp(date, curve_mu, buysell, curve_flc)

#2.2输入第二次操作信息，操作日为20200722
date=datetime.datetime.strptime('20200722','%Y%m%d')
curve_mu={'0':0.014747,'3M':0.019423,'6M':0.020547,'9M':0.021818,'1Y':0.022109,'2Y':0.026011,'3Y':0.027809,'4Y':0.031618,'5Y':0.032202,'10Y':0.038510}
curve_flc={'0':0.0002,'3M':0.0002,'6M':0.0002,'9M':0.0002,'1Y':0.0002,'2Y':0.0002,'3Y':0.0002,'4Y':0.0002,'5Y':0.0002,'10Y':0.0002}
buysell={'190215':100,'200203':100}
hdp_med=FXIncome.hdp(date, curve_mu, buysell, curve_flc)

#2.3输入第三次操作信息，操作日为20251021
date=datetime.datetime.strptime('20251021','%Y%m%d')
curve_mu={'0':0.014747,'3M':0.019423,'6M':0.020547,'9M':0.021818,'1Y':0.022109,'2Y':0.026011,'3Y':0.027809,'4Y':0.031618,'5Y':0.032202,'10Y':0.038510}
curve_flc={'0':0.0002,'3M':0.0002,'6M':0.0002,'9M':0.0002,'1Y':0.0002,'2Y':0.0002,'3Y':0.0002,'4Y':0.0002,'5Y':0.0002,'10Y':0.0002}
buysell={}
hdp_end=FXIncome.hdp(date, curve_mu, buysell, curve_flc)

#2.4将所有操作信息放到list里
hdplist=[hdp_begin, hdp_med, hdp_end]

#3进行proflio操作
#3.1输入信息，形成一个proflio类
myprofilo=FXIncome.profolio(assetlist, hdplist)
#3.2进行bsforcast_tpl实验
a=myprofilo.bsforcast_tpl()
#3.3进行bsforcast_plot实验
myprofilo.bsforcast_plot()
```

#### 原始bpforcast_oci使用案例

与bpforcast_tpl类似，主要区别是这里买入债券会以新的债券编码独立记一个asset，方便会计核算。值得一提的是，这个例子里面的oci债券包含了很多未实现的浮动盈亏，所以一卖就能实现很多价差收益

```python
import FXIncome
import datetime
#1输入资产信息（当前只支持债券）
#1.1输入第一只债券190214
code='190214'
ctype='附息'
initialdate=datetime.datetime.strptime('20191025','%Y%m%d')
enddate=datetime.datetime.strptime('20221025','%Y%m%d')
facevalue=250000000
couponrate=0.0297
assementdate=datetime.datetime.strptime('20200117','%Y%m%d')

curve={'0':0.004747,'3M':0.009423,'6M':0.010547,'9M':0.011818,'1Y':0.012109,'2Y':0.016011,'3Y':0.017809,'4Y':0.021618,'5Y':0.022202,'10Y':0.028510}
frequency=1
cleanprice=100.0317
asset_1=FXIncome.asset_bond(code, ctype, initialdate, enddate, facevalue, couponrate, assementdate, curve, frequency,cleanprice)
#1.2输入第二只债券190214-2（懒得想一只新的，就用一样的）
code='190214-copy'
ctype='附息'
initialdate=datetime.datetime.strptime('20191025','%Y%m%d')
enddate=datetime.datetime.strptime('20221025','%Y%m%d')
facevalue=250000000
couponrate=0.0297
assementdate=datetime.datetime.strptime('20200117','%Y%m%d')

curve={'0':0.004747,'3M':0.009423,'6M':0.010547,'9M':0.011818,'1Y':0.012109,'2Y':0.016011,'3Y':0.017809,'4Y':0.021618,'5Y':0.022202,'10Y':0.028510}
frequency=1
cleanprice=100.0317
asset_2=FXIncome.asset_bond(code, ctype, initialdate, enddate, facevalue, couponrate, assementdate, curve, frequency,cleanprice)

#1.3将所有资产放到list里
assetlist=[asset_1,asset_2]



#2输入操作信息
#2.1输入第一次操作信息
date=datetime.datetime.strptime('20200410','%Y%m%d')
curve_mu={'0':0.018,'3M':0.018,'6M':0.018,'9M':0.018,'1Y':0.018,'2Y':0.018,'3Y':0.018,'4Y':0.018,'5Y':0.018,'10Y':0.018}
curve_flc={'0':0,'3M':0,'6M':0,'9M':0,'1Y':0,'2Y':0,'3Y':0,'4Y':0,'5Y':0,'10Y':0}
buysell={'190214':-50000000,'190214-copy':-50000000}
hdp_1=FXIncome.hdp(date, curve_mu, buysell, curve_flc)

#2.2输入第二次操作信息
date=datetime.datetime.strptime('20200415','%Y%m%d')
curve_mu={'0':0.018375,'3M':0.018375,'6M':0.018375,'9M':0.018375,'1Y':0.018375,'2Y':0.018375,'3Y':0.018375,'4Y':0.018375,'5Y':0.018375,'10Y':0.018375}
curve_flc={'0':0.0002,'3M':0.0002,'6M':0.0002,'9M':0.0002,'1Y':0.0002,'2Y':0.0002,'3Y':0.0002,'4Y':0.0002,'5Y':0.0002,'10Y':0.0002}
buysell={'190214':55000000,'190214-copy':-55000000}
hdp_2=FXIncome.hdp(date, curve_mu, buysell, curve_flc)

#2.3输入第三次操作信息
date=datetime.datetime.strptime('20200415','%Y%m%d')
curve_mu={'0':0.0185,'3M':0.0185,'6M':0.0185,'9M':0.0185,'1Y':0.0185,'2Y':0.0185,'3Y':0.0185,'4Y':0.0185,'5Y':0.0185,'10Y':0.0185}
curve_flc={'0':0.0002,'3M':0.0002,'6M':0.0002,'9M':0.0002,'1Y':0.0002,'2Y':0.0002,'3Y':0.0002,'4Y':0.0002,'5Y':0.0002,'10Y':0.0002}
buysell={'190214':-50000000,'190214-copy':-50000000}
hdp_3=FXIncome.hdp(date, curve_mu, buysell, curve_flc)

date=datetime.datetime.strptime('20200415','%Y%m%d')
curve_mu={'0':0.0184,'3M':0.0184,'6M':0.0184,'9M':0.0184,'1Y':0.0184,'2Y':0.0184,'3Y':0.0184,'4Y':0.0184,'5Y':0.0184,'10Y':0.0184}
curve_flc={'0':0.0002,'3M':0.0002,'6M':0.0002,'9M':0.0002,'1Y':0.0002,'2Y':0.0002,'3Y':0.0002,'4Y':0.0002,'5Y':0.0002,'10Y':0.0002}
buysell={'190214':-45000000,'190214-copy':-45000000}
hdp_4=FXIncome.hdp(date, curve_mu, buysell, curve_flc)

date=datetime.datetime.strptime('20200415','%Y%m%d')
curve_mu={'0':0.0185,'3M':0.0185,'6M':0.0185,'9M':0.0185,'1Y':0.0185,'2Y':0.0185,'3Y':0.0185,'4Y':0.0185,'5Y':0.0185,'10Y':0.0185}
curve_flc={'0':0.0002,'3M':0.0002,'6M':0.0002,'9M':0.0002,'1Y':0.0002,'2Y':0.0002,'3Y':0.0002,'4Y':0.0002,'5Y':0.0002,'10Y':0.0002}
buysell={'190214':-50000000,'190214-copy':-50000000}
hdp_5=FXIncome.hdp(date, curve_mu, buysell, curve_flc)
#2.4将所有操作信息放到list里
hdplist=[hdp_1, hdp_2, hdp_3,hdp_4,hdp_5]
#3进行proflio操作
#3.1输入信息，形成一个proflio类
myprofilo=FXIncome.profolio(assetlist, hdplist)
#3.2进行bsforcast_oci实验
myprofilo.bsforcast_oci()
```

