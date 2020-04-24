# FXIncome（2.0）

当前版本主要是三个模块：（历史版本由于没有考虑模块化的结构，已经放弃）



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
    def ytm(self):
    def cashflow(self):
    def pv(self):
    def dv01(self):
   
```



##### 输入

* 大部分继承父类
* frequency 付息债券一年付息次数，其他类型债券用不上，统一填0

##### 输出

* change继承父类

* ytm输出根据收益率曲线计算的债券的收益率
* cashflow输出一个dic，每个key是datetime格式的日期，value是float格式的现金流
* pv输出一个两个元素的list，第一个元素是pv，第二个元素是一个dic，是将cashflow的现金流折现到assetmentdate。即第二个元素所有value的加和就是pv
* dv01输出债券的dv01

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

bsforcast_oci是***基于oci会计核算模式的结果***，下一个版本主要补充的地方

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



