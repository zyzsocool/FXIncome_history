from fxincome import *
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
    def __init__(self, assetlist, hdplist):
        self.asset_initial = copy.deepcopy(assetlist)
        self.asset_deal = copy.deepcopy(assetlist)
        self.asset_notdeal = copy.deepcopy(assetlist)
        self.hdp = hdplist

    def bsforcast_tpl(self, choice=None):
        self.asset_deal = copy.deepcopy(self.asset_initial)
        self.asset_notdeal = copy.deepcopy(self.asset_initial)
        pv_begin = 0
        resultall = []
        cashflow_his_deal = {}

        cashflow_his_notdeal = {}

        pv_end_notdeal = 0
        # 计算初始价值
        for asset in self.asset_deal:
            pv_begin += asset.pv_individual()[0]

        for hdp in self.hdp:
            cashflow_for_deal = {}
            cashflow_for_notdeal = {}

            newdate = hdp.date
            if choice:
                newcurve = hdp.curvemo()
            else:
                newcurve = hdp.curve_mu
            pv_final = 0

            for asset, asset0 in zip(self.asset_deal, self.asset_notdeal):
                # 计算交易操作的结果（deal）
                if asset.code in hdp.buysell.keys():

                    asset_cashflow0 = asset.cashflow_individual()
                    asset.change(newdate=newdate, newcurve=newcurve)
                    asset_pv1 = asset.pv()[0]
                    cash = -asset_pv1 * hdp.buysell[asset.code]
                    asset.change(face_value_delta=hdp.buysell[asset.code])
                    if hdp.date in cashflow_his_deal.keys():
                        cashflow_his_deal[hdp.date] += cash
                    else:
                        cashflow_his_deal[hdp.date] = cash
                    for i, j in asset_cashflow0.items():
                        if (i - hdp.date).days <= 0:
                            if i in cashflow_his_deal.keys():
                                cashflow_his_deal[i] += j
                            else:
                                cashflow_his_deal[i] = j
                else:
                    asset_cashflow0 = asset.cashflow_individual()
                    for i, j in asset_cashflow0.items():
                        if (i - hdp.date).days <= 0:
                            if i in cashflow_his_deal.keys():
                                cashflow_his_deal[i] += j
                            else:
                                cashflow_his_deal[i] = j
                    asset.change(newdate=newdate, newcurve=newcurve)
                    pv_final += asset.pv_individual()[0]
                # print('ytm（中间过程测试用，102行）:',asset.ytm())
                # print('pv（中间过程测试用，103行）',asset.pv()[0])

                for i, j in asset.pv_individual()[1].items():
                    if i != asset.assement_date:
                        if i in cashflow_for_deal:
                            cashflow_for_deal[i] += j
                        else:
                            cashflow_for_deal[i] = j

                # 计算不交易操作的结果（notdeal）
                asset_cashflow0 = asset0.cashflow_individual()
                for i, j in asset_cashflow0.items():
                    if (i - newdate).days <= 0:
                        if i in cashflow_his_notdeal.keys():
                            cashflow_his_notdeal[i] += j
                        else:
                            cashflow_his_notdeal[i] = j
                asset0.change(newdate=newdate, newcurve=newcurve)
                asset_cashflow1 = asset0.pv_individual()[1]
                for i, j in asset_cashflow1.items():
                    if i != asset.assement_date:
                        if i in cashflow_for_notdeal.keys():
                            cashflow_for_notdeal[i] += j
                        else:
                            cashflow_for_notdeal[i] = j

                pv_end_notdeal += asset0.pv_individual()[0]

            cash_end_deal = sum(cashflow_his_deal.values())
            pv_end_deal = sum(cashflow_for_deal.values())
            cash_end_notdeal = sum(cashflow_his_notdeal.values())
            pv_end_notdeal = sum(cashflow_for_notdeal.values())

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
            for m in self.asset_deal:
                if m.face_value != 0 and (m.end_date - lastdate).days > 0:
                    print(m.code, m.face_value)
        return resultall

    def bsforcast_tpl_plot(self, num=1000):

        result = self.bsforcast_tpl()[-1]
        deal_profit = []
        notdeal_profit = []
        div = []
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

        figure = plt.figure(1)
        date0 = self.hdp[0].date.strftime('%Y%m%d')
        date1 = self.hdp[-1].date.strftime('%Y%m%d')
        figure.suptitle('TPL持有期收益测试[%s--%s]（实验次数：%d）' % (date0, date1, num))

        ax1 = plt.subplot(1, 2, 1)
        ax2 = plt.subplot(1, 2, 2)

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

        plt.sca(ax2)

        plt.hist(div, histtype='stepfilled', alpha=0.3, density=1,
                 bins=200, color='green', label='操作与不操作之差（均值:' + str(a - b) + '万元）')

        plt.legend(loc=1)
        plt.xlabel('损益差(元)')
        plt.ylabel('相对频率')
        plt.title('损益差相对频率图')

        plt.show()

        return result

    def bsforcast_oci(self, choice=None):
        self.asset_deal = copy.deepcopy(self.asset_initial)
        self.asset_notdeal = copy.deepcopy(self.asset_initial)
        pv_begin = 0
        resultall = []
        cashflow_his_deal = {}

        cashflow_his_notdeal = {}
        interestgain_deal = 0
        pricegain_deal = 0

        pricegain_notdeal = 0

        pv_end_notdeal = 0
        # 计算初始价值
        for asset in self.asset_deal:
            pv_begin += asset.pv_individual()[0]

        for hdp in self.hdp:
            cashflow_for_deal = {}
            cashflow_for_notdeal = {}

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
            dontlist = []
            for asset, asset0 in zip(self.asset_deal, self.asset_notdeal):
                # 计算交易操作的结果（deal）
                if asset.code in hdp.buysell.keys():

                    if hdp.buysell[asset.code] > 0:

                        assetlist = []
                        for name in self.asset_deal:
                            assetlist.append(name.code)
                        k = 0
                        while True:
                            k += 1
                            code = asset.code + '-' + str(k)

                            if code not in assetlist:
                                break

                        ctype = asset.ctype
                        initialdate = asset.initial_date
                        enddate = asset.end_date
                        facevalue = hdp.buysell[asset.code]
                        couponrate = asset.coupon_rate
                        assementdate = hdp.date
                        curve = newcurve
                        frequency = asset.frequency
                        assetappend = Bond(
                            code,
                            ctype,
                            initialdate,
                            enddate,
                            facevalue,
                            couponrate,
                            assementdate,
                            curve,
                            frequency)
                        assetappend.cleanprice_fill()

                        self.asset_deal.append(assetappend)

                        asset_pv1 = assetappend.pv()[0]
                        cash = -asset_pv1 * hdp.buysell[asset.code]
                        asset_cashflow0 = assetappend.cashflow_individual()

                        facevalue = 0
                        assetappend2 = Bond(
                            code,
                            ctype,
                            initialdate,
                            enddate,
                            facevalue,
                            couponrate,
                            assementdate,
                            curve,
                            frequency)
                        assetappend2.cleanprice_fill()
                        self.asset_notdeal.append(assetappend2)

                        asset.change(newdate=newdate, newcurve=newcurve)

                        cleanprice_market1 = asset.cleanprice_func_individual()
                        cleanprice_def1 = asset.cleanprice_interestgain_individual()[0]
                        floatinggain_deal += (cleanprice_market1 -
                                              cleanprice_def1)

                        interestgain_deal += asset.cleanprice_interestgain_individual()[1]
                        interestgain_deal_div += asset.cleanprice_interestgain_individual()[
                            1]

                        pv_final += asset.pv_individual()[0]
                        if hdp.date in cashflow_his_deal.keys():
                            cashflow_his_deal[hdp.date] += cash
                        else:
                            cashflow_his_deal[hdp.date] = cash
                        for i, j in asset_cashflow0.items():
                            if (i - hdp.date).days <= 0:
                                if i in cashflow_his_deal.keys():
                                    cashflow_his_deal[i] += j
                                else:
                                    cashflow_his_deal[i] = j
                    else:
                        sellvol = hdp.buysell[asset.code]
                        asset_in = asset
                        k = 0

                        while sellvol < 0:
                            if sellvol + asset_in.face_value <= 0:
                                sellvol_in = -asset_in.face_value
                                sellvol -= sellvol_in
                            else:
                                sellvol_in = sellvol
                                sellvol = 0

                            asset_cashflow0 = asset_in.cashflow_individual()
                            asset_in.change(newdate=newdate, newcurve=newcurve)
                            asset_pv1 = asset_in.pv()[0]
                            cash = -asset_pv1 * sellvol_in

                            cleanprice_market0 = asset_in.cleanprice_func_individual()
                            cleanprice_def0 = asset_in.cleanprice_interestgain_individual()[
                                0]
                            interestgain_deal += asset_in.cleanprice_interestgain_individual()[
                                1]

                            asset_in.change(face_value_delta=sellvol_in)

                            cleanprice_market1 = asset_in.cleanprice_func_individual()
                            cleanprice_def1 = asset_in.cleanprice_interestgain_individual()[
                                0]
                            interestgain_deal_div += asset_in.cleanprice_interestgain_individual()[
                                1]
                            pricegain = (cleanprice_market0 - cleanprice_def0) - \
                                        (cleanprice_market1 - cleanprice_def1)
                            pricegain_deal += pricegain
                            floatinggain_deal += (cleanprice_market1 -
                                                  cleanprice_def1)
                            if sellvol != 0:
                                k += 1
                                code = asset_in.code + '-' + str(k)
                                for mmm in self.asset_deal:
                                    if code == mmm.code:
                                        asset_in = mmm
                                dontlist.append(code)

                            if hdp.date in cashflow_his_deal.keys():
                                cashflow_his_deal[hdp.date] += cash
                            else:
                                cashflow_his_deal[hdp.date] = cash
                            for i, j in asset_cashflow0.items():
                                if (i - hdp.date).days <= 0:
                                    if i in cashflow_his_deal.keys():
                                        cashflow_his_deal[i] += j
                                    else:
                                        cashflow_his_deal[i] = j

                elif asset.code not in dontlist:
                    asset_cashflow0 = asset.cashflow_individual()
                    for i, j in asset_cashflow0.items():
                        if (i - hdp.date).days <= 0:
                            if i in cashflow_his_deal.keys():
                                cashflow_his_deal[i] += j
                            else:
                                cashflow_his_deal[i] = j
                    asset.change(newdate=newdate, newcurve=newcurve)

                    cleanprice_market1 = asset.cleanprice_func_individual()
                    cleanprice_def1 = asset.cleanprice_interestgain_individual()[0]
                    floatinggain_deal += (cleanprice_market1 - cleanprice_def1)

                    interestgain_deal += asset.cleanprice_interestgain_individual()[1]
                    interestgain_deal_div += asset.cleanprice_interestgain_individual()[1]

                    pv_final += asset.pv_individual()[0]

                for i, j in asset.pv_individual()[1].items():
                    if i != asset.assement_date:
                        if i in cashflow_for_deal:
                            cashflow_for_deal[i] += j
                        else:
                            cashflow_for_deal[i] = j
                # 计算不交易操作的结果（notdeal）
                asset_cashflow0 = asset0.cashflow_individual()
                for i, j in asset_cashflow0.items():
                    if (i - newdate).days <= 0:
                        if i in cashflow_his_notdeal.keys():
                            cashflow_his_notdeal[i] += j
                        else:
                            cashflow_his_notdeal[i] = j
                asset0.change(newdate=newdate, newcurve=newcurve)
                asset_cashflow1 = asset0.pv_individual()[1]
                for i, j in asset_cashflow1.items():
                    if i != asset.assement_date:
                        if i in cashflow_for_notdeal.keys():
                            cashflow_for_notdeal[i] += j
                        else:
                            cashflow_for_notdeal[i] = j
                cleanprice_market1 = asset0.cleanprice_func_individual()
                cleanprice_def1 = asset0.cleanprice_interestgain_individual()[0]
                interestgain_notdeal += asset0.cleanprice_interestgain_individual()[1]

                floatinggain_notdeal += cleanprice_market1 - cleanprice_def1

                pv_end_notdeal += asset0.pv_individual()[0]

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
            interestgain_deal -= interestgain_deal_div

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
            for m in self.asset_deal:
                if m.face_value != 0 and (m.end_date - lastdate).days > 0:
                    print(m.code, m.face_value)
        return resultall

    def bsforcast_oci_plot(self, num=1000):

        result = self.bsforcast_oci()[-1]
        deal_profit = []
        deal_interest = []
        deal_price_floating = []

        notdeal_profit = []
        notdeal_interest = []
        notdeal_price_floating = []

        div_profit = []
        div_interest = []
        div_price_floating = []
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

        figure = plt.figure(1)
        date0 = self.hdp[0].date.strftime('%Y%m%d')
        date1 = self.hdp[-1].date.strftime('%Y%m%d')
        figure.suptitle('OCI持有期收益测试[%s--%s]（实验次数：%d）' % (date0, date1, num))

        ax1 = plt.subplot(2, 3, 1)
        ax2 = plt.subplot(2, 3, 2)
        ax3 = plt.subplot(2, 3, 3)
        ax4 = plt.subplot(2, 3, 4)
        ax5 = plt.subplot(2, 3, 5)
        ax6 = plt.subplot(2, 3, 6)

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

        plt.sca(ax4)
        c = a - b
        plt.hist(div_interest, histtype='stepfilled', alpha=0.3, density=1,
                 bins=200, color='g', label='操作与不操作差（均值:' + str(c) + '万元）')
        plt.xlabel('损益(元)')
        plt.title('利息收入差相对频率图')
        plt.ylabel('相对频率')
        plt.legend(loc=1)

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

        plt.sca(ax5)
        c = a - b
        plt.hist(div_price_floating, histtype='stepfilled', alpha=0.3, density=1,
                 bins=200, color='g', label='操作与不操作差（均值:' + str(c) + '万元）')
        plt.xlabel('损益(元)')
        plt.title('价差收入与浮动盈亏差相对频率图')
        plt.ylabel('相对频率')
        plt.legend(loc=1)

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

        plt.sca(ax6)
        c = a - b
        plt.hist(div_profit, histtype='stepfilled', alpha=0.3, density=1,
                 bins=200, color='g', label='操作与不操作差（均值:' + str(c) + '万元）')
        plt.xlabel('损益(元)')
        plt.title('损益总计差相对频率图')
        plt.ylabel('相对频率')
        plt.legend(loc=1)

        plt.show()

        return result

    def stresstest(self):
        pass
