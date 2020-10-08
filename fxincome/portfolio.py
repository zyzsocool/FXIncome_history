from fxincome.position import *
from fxincome.asset import *
from random import gauss
import copy
from tqdm import tqdm
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号


class Hdp:
    def __init__(self, date, curve_mu, buysell, curve_flc={}):
        self.date = date
        self.curve_mu = curve_mu
        self.curve_flc = curve_flc
        self.buysell = buysell

    def curvemo(self):
        curvemo0 = {}
        for i, j in self.curve_mu.items():
            curvemo0[i] = j + gauss(0, self.curve_flc[i] / 1.96)
        return curvemo0


class Portfolio:
    def __init__(self, positionlist, hdplist):
        self.position_initial = copy.deepcopy(positionlist)
        self.position_deal = copy.deepcopy(positionlist)
        self.position_notdeal = copy.deepcopy(positionlist)
        self.hdp = hdplist

    def bsforcast_tpl(self, choice=None):
        """
        计算tpl核算模式下portfolio的收益
        :param choice:默认为None，即正常模式，不进行蒙特卡洛模拟，每次运算都会print出结果。反之进行模特卡罗模拟，每次运算不会print结果，用于画图。
        :return resultall:存放每一次操作结果的list，其中每个元素为一个dic（有多少个hdp就有多少个元素），每一个dic的结构为：
         {
         'end_date'：              结束日日期（每次操作都对应一个结束日）
         'pv_begin'：              初始日持仓价值（初始日只有一个）
         'cashflow_his_deal'：     交易情况下从初始交易日到结束日收到的现金流
         'cash_end_deal'：         交易情况下结束日时的现金头寸
         'cashflow_for_deal'：     交易情况下结束日时的持仓债券未来折现现金流
         'pv_end_deal'：           交易情况下结束日时的价值，包括现金头寸和债券头寸
         'cashflow_his_notdeal'：  不交易情况下从初始交易日到结束日收到的现金流
         'cash_end_notdeal'：      不交易情况下结束日时的现金头寸
         'cashflow_for_notdeal'：  不交易情况下结束日时的持仓债券未来折现现金流
         'pv_end_notdeal'：        不交易情况下结束日时的价值，包括现金头寸和债券头寸
         }

        """

        # 1初始化信息

        # 因为每进行一次运算完position都会变更，所以每次运算前先初始化position的信息
        self.position_deal = copy.deepcopy(self.position_initial)
        self.position_notdeal = copy.deepcopy(self.position_initial)
        resultall = []  # 存放每一次操作结果的list，其中每个元素为一个dic。（最终输出结果）
        pv_begin = 0  # 初始价值
        cashflow_his_deal = {}  # 进行交易情况下的历史现金流（包括买卖现金流和派息兑付）
        cashflow_his_notdeal = {}  # 不进行交易情况下的历史现金流（仅包括初始组合的派息兑付）

        # 2计算初始价值pv_begin
        for position in self.position_deal:
            pv_begin += position.pv()[0]

        # 3按时间顺序对hdp逐一计算，计算出resultall这个list里面的每个元素的信息（核心部分，其输出结构参考函数说明处）
        for hdp in self.hdp:
            cashflow_for_deal = {}  # 进行交易情况下的未来现金流（已折现）
            cashflow_for_notdeal = {}  # 不进行交易情况下的未来现金流（已折现）
            newdate = hdp.date
            if choice:
                newcurve = hdp.curvemo()
            else:
                newcurve = hdp.curve_mu

            for position, position0 in zip(self.position_deal, self.position_notdeal):
                # 3.1计算交易操作的结果（deal，用for循环中的position）
                # 3.1.1处理需交易的资产
                if position.asset.code in hdp.buysell.keys():
                    position_cashflow0 = position.cashflow()  # 记录开始日的债券未来现金流
                    position.change(newdate=newdate, newcurve=newcurve)  # 改变债券头寸的日期为结束日，收益率曲线为结束日的收益率曲线
                    asset_pv1 = position.asset.pv(position.assessment_date, position.curve)[0]

                    cash = -asset_pv1 * hdp.buysell[position.asset.code]  # 计算现金头寸变化
                    position.change(quantity_delta=hdp.buysell[position.asset.code])  # 改变债券头寸
                    # 3.1.1.1把债券买卖的流水写入历史现金流
                    if hdp.date in cashflow_his_deal.keys():
                        cashflow_his_deal[hdp.date] += cash
                    else:
                        cashflow_his_deal[hdp.date] = cash
                    # 3.1.1.2把债券派息兑付的流水写入历史现金流
                    for i, j in position_cashflow0.items():
                        if i <= hdp.date:
                            if i in cashflow_his_deal.keys():
                                cashflow_his_deal[i] += j
                            else:
                                cashflow_his_deal[i] = j
                # 3.1.2处理不需交易的资产（注：要分清交易操作和交易资产，每次交易操作中有进行交易的资产，也有不进行交易的资产）
                else:
                    position_cashflow0 = position.cashflow()  # 记录开始日的债券未来现金流
                    # 把债券派息兑付的流水写入历史现金流（不交易所以没有买卖流水现金流）
                    for i, j in position_cashflow0.items():
                        if i <= hdp.date:
                            if i in cashflow_his_deal.keys():
                                cashflow_his_deal[i] += j
                            else:
                                cashflow_his_deal[i] = j
                    position.change(newdate=newdate, newcurve=newcurve)
                # 3.1.3处理交易操作后持仓债券未来折现现金流（无论资产是否交易，处理的逻辑都是一样，所以合并处理）
                for i, j in position.pv()[1].items():
                    if i != position.assessment_date:
                        if i in cashflow_for_deal:
                            cashflow_for_deal[i] += j
                        else:
                            cashflow_for_deal[i] = j

                # 3.2计算不交易操作的结果（notdeal，用for循环中的position0）
                position_cashflow0 = position0.cashflow()  # 记录开始日的债券未来现金流
                # 3.2.1把债券派息兑付的流水写入历史现金流（不交易所以没有买卖流水现金流）
                for i, j in position_cashflow0.items():
                    if i <= newdate:
                        if i in cashflow_his_notdeal.keys():
                            cashflow_his_notdeal[i] += j
                        else:
                            cashflow_his_notdeal[i] = j
                position0.change(newdate=newdate, newcurve=newcurve)
                # 3.2.2计算结束日时持仓债券未来折现现金流
                asset_cashflow1 = position0.pv()[1]
                for i, j in asset_cashflow1.items():
                    if i != position.assessment_date:
                        if i in cashflow_for_notdeal.keys():
                            cashflow_for_notdeal[i] += j
                        else:
                            cashflow_for_notdeal[i] = j

            # 3.3对得到的结果进行进一步处理算出最终需要的值以便输出
            cash_end_deal = sum(cashflow_his_deal.values())  # 由于初始现金头寸为0，所以结束日现金头寸就是历史现金流累加
            pv_end_deal = sum(cashflow_for_deal.values())  # 结束日债券价值就是债券未来折现现金流的累加
            cash_end_notdeal = sum(cashflow_his_notdeal.values())
            pv_end_notdeal = sum(cashflow_for_notdeal.values())

            # 3.4正常模式下print出每一次操作的结果
            if not choice:
                print('>>>>>>>>>>-------------组合测试------------<<<<<<<<<<')
                print('结束日:', hdp.date)
                print('初始价值：', pv_begin)
                print('-------------1操作------------')
                print('结束日已获得现金流:', cashflow_his_deal)
                print('结束日现金头寸:', cash_end_deal)
                print('结束日未来折现现金流:', cashflow_for_deal)
                print('结束日债券价值:', pv_end_deal)
                print('操作收益:', pv_end_deal + cash_end_deal - pv_begin)
                print('-------------2不操作------------')
                print('结束日已获得现金流:', cashflow_his_notdeal)
                print('结束日现金头寸:', cash_end_notdeal)
                print('结束日未来折现现金流:', cashflow_for_notdeal)
                print('结束日债券价值:', pv_end_notdeal)
                print('不操作收益:', pv_end_notdeal + cash_end_notdeal - pv_begin)
                print('-------------3对比------------')
                print('操作净现金头寸:', cash_end_deal - cash_end_notdeal)
                print(
                    '操作净收益:',
                    pv_end_deal +
                    cash_end_deal -
                    pv_end_notdeal -
                    cash_end_notdeal)
            # 3.5记录好reuslt的dic结果并录入到输出的list中
            result = {}
            result['end_date'] = hdp.date
            result['pv_begin'] = pv_begin
            result['cashflow_his_deal'] = cashflow_his_deal
            result['cash_end_deal'] = cash_end_deal
            result['cashflow_for_deal'] = cashflow_for_deal
            result['pv_end_deal'] = pv_end_deal
            result['cashflow_his_notdeal'] = cashflow_his_notdeal
            result['cash_end_notdeal'] = cash_end_notdeal
            result['cashflow_for_notdeal'] = cashflow_for_notdeal
            result['pv_end_notdeal'] = pv_end_notdeal
            resultall.append(result)
        # 4正常模式下print所有操作的最终结果
        if not choice:

            print('--------------------最终日核算---------------')
            print('-------------1操作历史累计现金头寸------------')
            jj = 0
            cashflow_his_deal_list = sorted(cashflow_his_deal.keys())
            for i in cashflow_his_deal_list:
                if cashflow_his_deal[i] != 0:
                    jj += cashflow_his_deal[i]
                    print(i, jj)
            print('-------------2不操作历史累计现金头寸------------')
            jj = 0
            cashflow_his_notdeal_list = sorted(cashflow_his_notdeal.keys())
            for i in cashflow_his_notdeal_list:
                if cashflow_his_notdeal[i] != 0:
                    jj += cashflow_his_notdeal[i]
                    print(i, jj)
            print('-------------3操作后最终债券剩余面额------------')

            lastdate = hdp.date
            for m in self.position_deal:
                if m.quantity != 0 and m.asset.end_date > lastdate:
                    print(m.asset.code, m.quantity)
        # 5输出最终结果
        return resultall

    def bsforcast_tpl_plot(self, num=1000):
        """

        :param num: 进行蒙特卡洛模拟的次数，默认为1000，次数越多画图越好看，但是时间越慢
        :return result：和bsforcast_tpl()的输出结果一模一样
        画图：这个函数最重要的输出是那个频率分布直方图
        """

        # 1.进行一次正常模式下的bsforcast_tpl，以确定均值
        resultall = self.bsforcast_tpl()
        result = resultall[-1]
        # 2.进行多次画图模式下的bsforcast_tpl，得到多个样本
        # 2.1初始化几个list，记录每次计算的样本
        deal_profit = []
        notdeal_profit = []
        div = []
        # 2.2进行多次bsforcast_tpl计算
        for i in tqdm(range(0, num)):
            resultx = self.bsforcast_tpl(1)[-1]
            deal_profit.append(
                resultx['cash_end_deal'] +
                resultx['pv_end_deal'] -
                resultx['pv_begin'])
            notdeal_profit.append(
                resultx['cash_end_notdeal'] +
                resultx['pv_end_notdeal'] -
                resultx['pv_begin'])
            div.append(
                resultx['cash_end_deal'] +
                resultx['pv_end_deal'] -
                resultx['cash_end_notdeal'] -
                resultx['pv_end_notdeal'])

        # 3画图
        # 3.1准备总图要素
        figure = plt.figure(1)
        date0 = self.hdp[0].date.strftime('%Y%m%d')
        date1 = self.hdp[-1].date.strftime('%Y%m%d')
        figure.suptitle('TPL持有期收益测试[%s--%s]（实验次数：%d）' % (date0, date1, num))

        # 3.2将图分为两块
        ax1 = plt.subplot(1, 2, 1)
        ax2 = plt.subplot(1, 2, 2)

        # 3.2.1画第一个图
        plt.sca(ax1)

        a = int((result['cash_end_deal'] + result['pv_end_deal'] - result['pv_begin']) / 10000)
        b = int((result['cash_end_notdeal'] + result['pv_end_notdeal'] - result['pv_begin']) / 10000)

        plt.hist(deal_profit, histtype='stepfilled', alpha=0.3, density=1,
                 bins=200, label='操作（均值:' + str(a) + '万元）')
        plt.hist(notdeal_profit, histtype='stepfilled', alpha=0.3, density=1,
                 bins=200, label='不操作（均值:' + str(b) + '万元）')
        plt.xlabel('损益(元)')
        plt.title('损益相对频率图')

        plt.ylabel('相对频率')
        plt.legend(loc=1)

        # 3.2.2画第二个图
        plt.sca(ax2)

        plt.hist(div, histtype='stepfilled', alpha=0.3, density=1,
                 bins=200, color='green', label='操作与不操作之差（均值:' + str(a - b) + '万元）')

        plt.legend(loc=1)
        plt.xlabel('损益差(元)')
        plt.ylabel('相对频率')
        plt.title('损益差相对频率图')

        # 3.3输出图
        plt.show()

        # 4输出结果
        return resultall

    def bsforcast_oci(self, choice=None):
        """
        计算oci核算模式下portfolio的收益
        :param choice:默认为None，即正常模式，不进行蒙特卡洛模拟，每次运算都会print出结果。反之进行模特卡罗模拟，每次运算不会print结果，用于画图。
        :return resultall:存放每一次操作结果的list，其中每个元素为一个dic（有多少个hdp就有多少个元素），每一个dic的结构为：
         {
         'end_date'：              结束日日期（每次操作都对应一个结束日）
         'pv_begin'：              初始日持仓价值（初始日只有一个）
         'cashflow_his_deal'：     交易情况下从初始交易日到结束日收到的现金流
         'cash_end_deal'：         交易情况下结束日时的现金头寸
         'cashflow_for_deal'：     交易情况下结束日时的持仓债券未来折现现金流
         'pv_end_deal'：           交易情况下结束日时的价值，包括现金头寸和债券头寸
         'pricegain_deal'：        交易情况下交易价差收益
         'floatinggain_deal'：     交易情况下浮动盈亏
         'interestgain_deal'：     交易情况下利息收益
         'cashflow_his_notdeal'：  不交易情况下从初始交易日到结束日收到的现金流
         'cash_end_notdeal'：      不交易情况下结束日时的现金头寸
         'cashflow_for_notdeal'：  不交易情况下结束日时的持仓债券未来折现现金流
         'pv_end_notdeal'：        不交易情况下结束日时的价值，包括现金头寸和债券头寸
         'pricegain_deal'：        不交易情况下交易价差收益
         'floatinggain_deal'：     不交易情况下浮动盈亏
         'interestgain_deal'：     不交易情况下利息收益
         }
        """

        # 1初始化信息
        # 因为每进行一次运算完position都会变更，所以每次运算前先初始化position的信息
        self.position_deal = copy.deepcopy(self.position_initial)
        self.position_notdeal = copy.deepcopy(self.position_initial)
        resultall = []  # 存放每一次操作结果的list，其中每个元素为一个dic。（最终输出结果）
        pv_begin = 0  # 初始价值
        cashflow_his_deal = {}  # 进行交易情况下的历史现金流（包括买卖现金流和派息兑付）
        cashflow_his_notdeal = {}  # 不进行交易情况下的历史现金流（仅包括初始组合的派息兑付）
        interestgain_deal = 0  # 交易情况下利息收入
        pricegain_deal = 0  # 交易情况下价差收入
        pricegain_notdeal = 0

        # 2计算初始价值pv_begin
        for position in self.position_deal:
            pv_begin += position.pv()[0]

        # 3按时间顺序对hdp逐一计算，计算出resultall这个list里面的每个元素的信息（核心部分，其输出结构参考函数说明处）
        for hdp in self.hdp:
            cashflow_for_deal = {}  # 进行交易情况下的未来现金流（已折现）
            cashflow_for_notdeal = {}  # 不进行交易情况下的未来现金流（已折现）

            newdate = hdp.date
            if choice:
                newcurve = hdp.curvemo()
            else:
                newcurve = hdp.curve_mu
            pv_final = 0

            interestgain_deal_div = 0
            floatinggain_deal = 0
            floatinggain_notdeal = 0
            interestgain_notdeal = 0
            dontlist = []  # 在3.1.1.2卖出资产的情况中，一个资产如果卖了一些，那么程序也会将它的流水和损益处理好
            # 为了防止后面3.1.2中重复处理，所以设置这个list，卖了之后就把资产代码放进这个list里，3.1.2只处理不在list里的资产
            for position, position0 in zip(self.position_deal, self.position_notdeal):
                # 3.1计算交易操作的结果（deal，用for循环中的position）
                # 3.1.1处理需交易的资产
                if position.asset.code in hdp.buysell.keys():
                    # 3.1.1.1买入资产的情况
                    if hdp.buysell[position.asset.code] > 0:
                        # 3.1.1.1.1确定买入资产的新code，比如存在190210，和190210-1，则新建一个190210-2
                        positionlist = []
                        for name in self.position_deal:
                            positionlist.append(name.asset.code)
                        k = 0
                        while True:
                            k += 1
                            code = position.asset.code + '-' + str(k)

                            if code not in positionlist:
                                break
                        # 3.1.1.1.2将新买入资产放入position_deal(这个新的资产会在下个循环时在3.1.2不需交易的资产中处理)
                        ctype = position.asset.ctype
                        initialdate = position.asset.initial_date
                        enddate = position.asset.end_date
                        quantity = hdp.buysell[position.asset.code]
                        couponrate = position.asset.coupon_rate
                        assessment_date = hdp.date
                        curve = newcurve
                        frequency = position.asset.frequency
                        assetappend = Bond(
                            code,
                            ctype,
                            initialdate,
                            enddate,
                            couponrate,
                            frequency)
                        positionappend = PositionBond(assetappend, quantity, assessment_date, curve)
                        self.position_deal.append(positionappend)

                        position_pv1 = positionappend.asset.pv(positionappend.assessment_date, positionappend.curve)[0]
                        cash = -position_pv1 * hdp.buysell[position.asset.code]
                        position_cashflow0 = positionappend.cashflow()

                        # 3.1.1.1.3将新买入资产放入position_notdeal（为了两个list大小一致，因此quantity定为0，相当于没有买入）
                        quantity = 0
                        assetappend2 = Bond(
                            code,
                            ctype,
                            initialdate,
                            enddate,
                            couponrate,
                            frequency)
                        positionappend2 = PositionBond(assetappend2, quantity, assessment_date, curve)
                        self.position_notdeal.append(positionappend2)

                        position.change(newdate=newdate, newcurve=newcurve)

                        # 3.1.1.1.4计算原来资产的浮动盈亏、利息收入
                        cleanprice_market1 = position.asset.pv_cleanprice(position.assessment_date,
                                                                          position.curve) * position.quantity
                        cleanprice_def1 = position.cleanprice_interestgain()[0]
                        floatinggain_deal += (cleanprice_market1 - cleanprice_def1)  # 计算浮动盈亏

                        interestgain_deal += position.cleanprice_interestgain()[1]  # 计算利息收入
                        interestgain_deal_div += position.cleanprice_interestgain()[1]  # 这里面有骚操作

                        pv_final += position.pv()[0]
                        # 3.1.1.1.5把债券买卖的流水写入历史现金流
                        if hdp.date in cashflow_his_deal.keys():
                            cashflow_his_deal[hdp.date] += cash
                        else:
                            cashflow_his_deal[hdp.date] = cash
                        # 3.1.1.1.6把债券派息兑付的流水写入历史现金流
                        for i, j in position_cashflow0.items():
                            if i <= hdp.date:
                                if i in cashflow_his_deal.keys():
                                    cashflow_his_deal[i] += j
                                else:
                                    cashflow_his_deal[i] = j
                    # 3.1.1.2卖出资产的情况
                    else:
                        # 3.1.1.2.1
                        sellvol = hdp.buysell[position.asset.code]
                        position_in = position  # 先处理position的，卖完了后面while循环会继续卖另外的
                        k = 0

                        while sellvol < 0:
                            if sellvol + position_in.quantity <= 0:  # 1900210卖完了还不够，就卖190210-1
                                sellvol_in = -position_in.quantity  # 把能卖的全部卖完
                                sellvol -= sellvol_in  # 还要卖的就留到下个循环卖-1，-2，-3……的
                            else:
                                sellvol_in = sellvol  # 能卖完就卖
                                sellvol = 0

                            position_cashflow0 = position_in.cashflow()
                            position_in.change(newdate=newdate, newcurve=newcurve)
                            position_pv1 = position_in.asset.pv(position_in.assessment_date, position_in.curve)[0]
                            cash = -position_pv1 * sellvol_in

                            cleanprice_market0 = position_in.asset.pv_cleanprice(position.assessment_date,
                                                                                 position.curve) * position_in.quantity
                            cleanprice_def0 = position_in.cleanprice_interestgain()[0]
                            interestgain_deal += position_in.cleanprice_interestgain()[1]

                            position_in.change(quantity_delta=sellvol_in)

                            cleanprice_market1 = position_in.asset.pv_cleanprice(position.assessment_date,
                                                                                 position.curve) * position_in.quantity
                            cleanprice_def1 = position_in.cleanprice_interestgain()[0]
                            interestgain_deal_div += position_in.cleanprice_interestgain()[1]  # 这里面有骚操作
                            # 价差收入和浮动盈亏就是一样东西，所以要看卖了多少分配到两边
                            pricegain = (cleanprice_market0 - cleanprice_def0) - (
                                        cleanprice_market1 - cleanprice_def1)  # 计算价差收入
                            pricegain_deal += pricegain
                            floatinggain_deal += (cleanprice_market1 - cleanprice_def1)  # 计算浮动盈亏
                            # 没卖完的话就卖下一个
                            if sellvol != 0:
                                k += 1
                                code = position_in.asset.code + '-' + str(k)
                                for mmm in self.position_deal:
                                    if code == mmm.asset.code:
                                        position_in = mmm
                                dontlist.append(code)  # 资产卖过一次之后其实就算过各种现金流和收益了，所以就放入dontlist，不要再在3.1.2中处理了

                            # 把债券买卖的流水写入历史现金流
                            if hdp.date in cashflow_his_deal.keys():
                                cashflow_his_deal[hdp.date] += cash
                            else:
                                cashflow_his_deal[hdp.date] = cash
                            # 把债券派息兑付的流水写入历史现金流
                            for i, j in position_cashflow0.items():
                                if i <= hdp.date:
                                    if i in cashflow_his_deal.keys():
                                        cashflow_his_deal[i] += j
                                    else:
                                        cashflow_his_deal[i] = j

                # 3.1.2处理不需交易的资产（注：要分清交易操作和交易资产，每次交易操作中有进行交易的资产，也有不进行交易的资产）
                elif position.asset.code not in dontlist:
                    position_cashflow0 = position.cashflow()
                    for i, j in position_cashflow0.items():
                        if i <= hdp.date:
                            if i in cashflow_his_deal.keys():
                                cashflow_his_deal[i] += j
                            else:
                                cashflow_his_deal[i] = j
                    position.change(newdate=newdate, newcurve=newcurve)

                    cleanprice_market1 = position.asset.pv_cleanprice(position.assessment_date,
                                                                      position.curve) * position.quantity
                    cleanprice_def1 = position.cleanprice_interestgain()[0]
                    floatinggain_deal += (cleanprice_market1 - cleanprice_def1)

                    interestgain_deal += position.cleanprice_interestgain()[1]
                    interestgain_deal_div += position.cleanprice_interestgain()[1]

                    pv_final += position.pv()[0]

                # 3.1.3处理交易操作后持仓债券未来折现现金流（无论资产是否交易，处理的逻辑都是一样，所以合并处理）
                for i, j in position.pv()[1].items():
                    if i != position.assessment_date:
                        if i in cashflow_for_deal:
                            cashflow_for_deal[i] += j
                        else:
                            cashflow_for_deal[i] = j
                # 3.2计算不交易操作的结果（notdeal，用for循环中的position0）
                # 3.2.1把债券派息兑付的流水写入历史现金流
                position_cashflow0 = position0.cashflow()
                for i, j in position_cashflow0.items():
                    if i <= newdate:
                        if i in cashflow_his_notdeal.keys():
                            cashflow_his_notdeal[i] += j
                        else:
                            cashflow_his_notdeal[i] = j
                position0.change(newdate=newdate, newcurve=newcurve)
                asset_cashflow1 = position0.pv()[1]
                # 3.2.2计算持仓债券未来折现现金流
                for i, j in asset_cashflow1.items():
                    if i != position.assessment_date:
                        if i in cashflow_for_notdeal.keys():
                            cashflow_for_notdeal[i] += j
                        else:
                            cashflow_for_notdeal[i] = j
                # 3.2.3计算浮动盈亏、利息收入
                cleanprice_market1 = position0.asset.pv_cleanprice(position0.assessment_date,
                                                                   position0.curve) * position0.quantity
                cleanprice_def1 = position0.cleanprice_interestgain()[0]
                interestgain_notdeal += position0.cleanprice_interestgain()[1]

                floatinggain_notdeal += cleanprice_market1 - cleanprice_def1

            cash_end_deal = sum(cashflow_his_deal.values())
            pv_end_deal = sum(cashflow_for_deal.values())
            cash_end_notdeal = sum(cashflow_his_notdeal.values())
            pv_end_notdeal = sum(cashflow_for_notdeal.values())

            if not choice:
                print('>>>>>>>>>>-------------组合测试------------<<<<<<<<<<')
                print('结束日:', hdp.date)
                print('-------------1操作------------')
                print('结束日已获得现金流:', cashflow_his_deal)
                print('结束日现金头寸:', cash_end_deal)
                print('结束日未来折现现金流:', cashflow_for_deal)
                print('结束日债券价值:', pv_end_deal)
                print('价差收益', pricegain_deal)
                print('浮动盈亏', floatinggain_deal)
                print('利息收益', interestgain_deal)
                print(
                    '损益总计',
                    pricegain_deal +
                    floatinggain_deal +
                    interestgain_deal)
                print('-------------2不操作------------')
                print('结束日已获得现金流:', cashflow_his_notdeal)
                print('结束日现金头寸:', cash_end_notdeal)
                print('结束日未来折现现金流:', cashflow_for_notdeal)
                print('结束日债券价值:', pv_end_notdeal)
                print('价差收益', pricegain_notdeal)
                print('浮动盈亏', floatinggain_notdeal)
                print('利息收益', interestgain_notdeal)
                print(
                    '损益总计',
                    pricegain_notdeal +
                    floatinggain_notdeal +
                    interestgain_notdeal)
                print('-------------3对比------------')
                print('操作净现金头寸:', cash_end_deal - cash_end_notdeal)
                print('操作净债券头寸:', pv_end_deal - pv_end_notdeal)
                print('操作净价差收益:', pricegain_deal - pricegain_notdeal)
                print('操作净浮动盈亏:', floatinggain_deal - floatinggain_notdeal)
                print('操作净利息收益:', interestgain_deal - interestgain_notdeal)
                print('操作净损益总计', pricegain_deal +
                      floatinggain_deal +
                      interestgain_deal -
                      (pricegain_notdeal +
                       floatinggain_notdeal +
                       interestgain_notdeal))
            result = {}
            result['end_date'] = hdp.date
            result['pv_begin'] = pv_begin
            result['cashflow_his_deal'] = cashflow_his_deal
            result['cash_end_deal'] = cash_end_deal
            result['cashflow_for_deal'] = cashflow_for_deal
            result['pv_end_deal'] = pv_end_deal

            result['pricegain_deal'] = pricegain_deal
            result['floatinggain_deal'] = floatinggain_deal
            result['interestgain_deal'] = interestgain_deal

            result['cashflow_his_notdeal'] = cashflow_his_notdeal
            result['cash_end_notdeal'] = cash_end_notdeal
            result['cashflow_for_notdeal'] = cashflow_for_notdeal
            result['pv_end_notdeal'] = pv_end_notdeal

            result['pricegain_notdeal'] = pricegain_notdeal
            result['floatinggain_notdeal'] = floatinggain_notdeal
            result['interestgain_notdeal'] = interestgain_notdeal

            resultall.append(result)
            interestgain_deal -= interestgain_deal_div  # 骚操作

        if not choice:
            print('--------------------最终日核算---------------')
            print('-------------1操作历史累计现金头寸------------')
            jj = 0
            cashflow_his_deal_list = sorted(cashflow_his_deal.keys())
            for i in cashflow_his_deal_list:
                if cashflow_his_deal[i] != 0:
                    jj += cashflow_his_deal[i]
                    print(i, jj)

            print('-------------2不操作历史累计现金头寸------------')
            jj = 0
            cashflow_his_notdeal_list = sorted(cashflow_his_notdeal.keys())
            for i in cashflow_his_notdeal_list:
                if cashflow_his_notdeal[i] != 0:
                    jj += cashflow_his_notdeal[i]
                    print(i, jj)
            print('-------------3操作后最终债券剩余面额------------')

            lastdate = hdp.date
            for m in self.position_deal:
                if m.quantity != 0 and m.asset.end_date > lastdate:
                    print(m.asset.code, m.quantity)
        return resultall

    def bsforcast_oci_plot(self, num=1000):
        """

        :param num: 进行蒙特卡洛模拟的次数，默认为1000，次数越多画图越好看，但是时间越慢
        :return: 和bsforcast_oci()的输出结果一模一样
        画图：这个函数最重要的输出是那个频率分布直方图
        """

        # 1.进行一次正常模式下的bsforcast_oci，以确定均值
        resultall = self.bsforcast_oci()
        result = resultall[-1]
        deal_profit = []
        deal_interest = []
        deal_price_floating = []
        # 2.进行多次画图模式下的bsforcast_oci，得到多个样本
        # 2.1初始化几个list，记录每次计算的样本

        notdeal_profit = []
        notdeal_interest = []
        notdeal_price_floating = []

        div_profit = []
        div_interest = []
        div_price_floating = []
        # 2.2进行多次bsforcast_oci计算
        for i in tqdm(range(0, num)):
            resultx = self.bsforcast_oci(1)[-1]
            deal_profit.append(
                resultx['pricegain_deal'] +
                resultx['floatinggain_deal'] +
                resultx['interestgain_deal'])
            deal_interest.append(resultx['interestgain_deal'])
            deal_price_floating.append(
                resultx['pricegain_deal'] +
                resultx['floatinggain_deal'])

            notdeal_profit.append(
                resultx['pricegain_notdeal'] +
                resultx['floatinggain_notdeal'] +
                resultx['interestgain_notdeal'])
            notdeal_interest.append(resultx['interestgain_notdeal'])
            notdeal_price_floating.append(
                resultx['pricegain_notdeal'] +
                resultx['floatinggain_notdeal'])

            div_profit.append(deal_profit[-1] - notdeal_profit[-1])
            div_interest.append(deal_interest[-1] - notdeal_interest[-1])
            div_price_floating.append(deal_price_floating[-1] - notdeal_price_floating[-1])

        # 3画图
        # 3.1准备总图要素
        figure = plt.figure(1)
        date0 = self.hdp[0].date.strftime('%Y%m%d')
        date1 = self.hdp[-1].date.strftime('%Y%m%d')
        figure.suptitle('OCI持有期收益测试[%s--%s]（实验次数：%d）' % (date0, date1, num))

        # 3.2将图分为六块
        ax1 = plt.subplot(2, 3, 1)
        ax2 = plt.subplot(2, 3, 2)
        ax3 = plt.subplot(2, 3, 3)
        ax4 = plt.subplot(2, 3, 4)
        ax5 = plt.subplot(2, 3, 5)
        ax6 = plt.subplot(2, 3, 6)

        # 3.2.1画第一个图
        plt.sca(ax1)
        a = int(result['interestgain_deal'] / 10000)
        b = int(result['interestgain_notdeal'] / 10000)
        plt.hist(deal_interest, histtype='stepfilled', alpha=0.3, density=1,
                 bins=200, label='操作（均值:' + str(a) + '万元）')
        # plt.hist(notdeal_interest, histtype='stepfilled', alpha=0.3, density=1,
        #           bins=200, label='不操作（固定值:' + str(b) + '万元）')

        plt.xlabel('损益(元)[不操作（固定值:' + str(b) + '万元）]')
        plt.title('利息收入相对频率图')
        plt.ylabel('相对频率')
        plt.legend(loc=1)

        # 3.2.2画第二个图
        plt.sca(ax4)
        c = a - b
        plt.hist(div_interest, histtype='stepfilled', alpha=0.3, density=1,
                 bins=200, color='g', label='操作与不操作差（均值:' + str(c) + '万元）')
        plt.xlabel('损益(元)')
        plt.title('利息收入差相对频率图')
        plt.ylabel('相对频率')
        plt.legend(loc=1)

        # 3.2.3画第三个图
        plt.sca(ax2)
        a = int((result['pricegain_deal'] + result['floatinggain_deal']) / 10000)
        b = int((result['pricegain_notdeal'] + result['floatinggain_notdeal']) / 10000)
        plt.hist(deal_price_floating, histtype='stepfilled', alpha=0.3, density=1,
                 bins=200, label='操作（均值:' + str(a) + '万元）')
        plt.hist(notdeal_price_floating, histtype='stepfilled', alpha=0.3, density=1,
                 bins=200, label='不操作（均值:' + str(b) + '万元）')
        plt.xlabel('损益(元)')
        plt.title('价差收入与浮动盈亏相对频率图')
        plt.ylabel('相对频率')
        plt.legend(loc=1)

        # 3.2.4画第四个图
        plt.sca(ax5)
        c = a - b
        plt.hist(div_price_floating, histtype='stepfilled', alpha=0.3, density=1,
                 bins=200, color='g', label='操作与不操作差（均值:' + str(c) + '万元）')
        plt.xlabel('损益(元)')
        plt.title('价差收入与浮动盈亏差相对频率图')
        plt.ylabel('相对频率')
        plt.legend(loc=1)

        # 3.2.5画第五个图
        plt.sca(ax3)
        a = int((result['pricegain_deal'] + result['floatinggain_deal'] + result['interestgain_deal']) / 10000)
        b = int((result['pricegain_notdeal'] + result['floatinggain_notdeal'] + result['interestgain_notdeal']) / 10000)
        plt.hist(deal_profit, histtype='stepfilled', alpha=0.3, density=1,
                 bins=200, label='操作（均值:' + str(a) + '万元）')
        plt.hist(notdeal_profit, histtype='stepfilled', alpha=0.3, density=1,
                 bins=200, label='不操作（均值:' + str(b) + '万元）')
        plt.xlabel('损益(元)')
        plt.title('损益总计相对频率图')

        plt.ylabel('相对频率')
        plt.legend(loc=1)

        # 3.2.6画第六个图
        plt.sca(ax6)
        c = a - b
        plt.hist(div_profit, histtype='stepfilled', alpha=0.3, density=1,
                 bins=200, color='g', label='操作与不操作差（均值:' + str(c) + '万元）')
        plt.xlabel('损益(元)')
        plt.title('损益总计差相对频率图')
        plt.ylabel('相对频率')
        plt.legend(loc=1)

        # 3.3输出图
        plt.show()

        # 4输出结果
        return resultall

    def stresstest(self):
        pass
