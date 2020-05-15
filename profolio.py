from random import gauss
import copy
from tqdm import tqdm
import matplotlib.pyplot as plt
import FXIncome

class hdp():
    def __init__(self,date,curve_mu,buysell,curve_flc={}):
        self.date=date
        self.curve_mu=curve_mu
        self.curve_flc=curve_flc
        self.buysell=buysell
    def curvemo(self):
        curvemo0={}
        for i,j in self.curve_mu.items():
            curvemo0[i]=j+gauss(0,self.curve_flc[i]/1.96)
        return curvemo0



class profolio():
    def __init__(self, assetlist, hdplist):
        self.asset_initial=copy.deepcopy(assetlist)
        self.asset_deal=copy.deepcopy(assetlist)
        self.asset_notdeal=copy.deepcopy(assetlist)
        self.hdp=hdplist

    def bsforcast_tpl(self, choice=None):
        self.asset_deal = copy.deepcopy(self.asset_initial)
        self.asset_notdeal = copy.deepcopy(self.asset_initial)
        pv_begin = 0
        resultall=[]
        cashflow_his_deal = {}

        cashflow_his_notdeal = {}





        pv_end_notdeal=0
        #计算初始价值
        for asset in self.asset_deal:
            pv_begin+=asset.pv()[0]



        for hdp in self.hdp:
            cashflow_for_deal = {}
            cashflow_for_notdeal = {}

            newdate=hdp.date
            if choice:
                newcurve=hdp.curvemo()
            else:
                newcurve=hdp.curve_mu
            pv_final=0


            for asset,asset0 in zip(self.asset_deal,self.asset_notdeal):
                # 计算交易操作的结果（deal）
                if asset.code in hdp.buysell.keys():


                    asset_cashflow0 = asset.cashflow()
                    asset.change(newdate=newdate, newcurve=newcurve)
                    asset_pv1=asset.pv(facetype=1)[0]
                    cash = -asset_pv1  * hdp.buysell[asset.code]
                    asset.change(facevaluedelta=hdp.buysell[asset.code])
                    if hdp.date in cashflow_his_deal.keys():
                        cashflow_his_deal[hdp.date] += cash
                    else:
                        cashflow_his_deal[hdp.date] = cash
                    for i,j in asset_cashflow0.items():
                        if (i-hdp.date).days<=0:
                            if i in cashflow_his_deal.keys():
                                cashflow_his_deal[i]+=j
                            else:
                                cashflow_his_deal[i] = j
                else:
                    asset_cashflow0 = asset.cashflow()
                    for i,j in asset_cashflow0.items():
                        if (i - hdp.date).days <= 0:
                            if i in cashflow_his_deal.keys():
                                cashflow_his_deal[i] += j
                            else:
                                cashflow_his_deal[i] = j
                    asset.change(newdate=newdate, newcurve=newcurve)
                    pv_final += asset.pv()[0]
                #print('ytm（中间过程测试用，102行）:',asset.ytm())
                #print('pv（中间过程测试用，103行）',asset.pv()[0])


                for i,j in asset.pv()[1].items():
                    if i!=asset.assementdate:
                        if i in cashflow_for_deal:
                            cashflow_for_deal[i]+=j
                        else:
                            cashflow_for_deal[i]=j




                #计算不交易操作的结果（notdeal）
                asset_cashflow0 = asset0.cashflow()
                for i, j in asset_cashflow0.items():
                    if (i-newdate).days<=0:
                        if i in cashflow_his_notdeal.keys():
                            cashflow_his_notdeal[i]+=j
                        else:
                            cashflow_his_notdeal[i]=j
                asset0.change(newdate=newdate,newcurve=newcurve)
                asset_cashflow1=asset0.pv()[1]
                for i, j in asset_cashflow1.items():
                    if i!=asset.assementdate:
                        if i in cashflow_for_notdeal.keys():
                            cashflow_for_notdeal[i]+=j
                        else:
                            cashflow_for_notdeal[i]=j


                pv_end_notdeal+=asset0.pv()[0]




            cash_end_deal=sum(cashflow_his_deal.values())
            pv_end_deal=sum(cashflow_for_deal.values())
            cash_end_notdeal=sum(cashflow_his_notdeal.values())
            pv_end_notdeal=sum(cashflow_for_notdeal.values())

            if not choice:
                print('>>>>>>>>>>-------------组合测试------------<<<<<<<<<<')
                print('结束日:',hdp.date)
                print('初始价值：',pv_begin)
                print('-------------1操作------------')
                print('结束日已获得现金流:',cashflow_his_deal)
                print('结束日现金头寸:',cash_end_deal)
                print('结束日未来折现现金流:',cashflow_for_deal)
                print('结束日债券价值:',pv_end_deal)
                print('操作收益:',pv_end_deal+cash_end_deal-pv_begin)
                print('-------------2不操作------------')
                print('结束日已获得现金流:',cashflow_his_notdeal)
                print('结束日现金头寸:', cash_end_notdeal)
                print('结束日未来折现现金流:', cashflow_for_notdeal)
                print('结束日债券价值:', pv_end_notdeal)
                print('不操作收益:',pv_end_notdeal+cash_end_notdeal-pv_begin)
                print('-------------3对比------------')
                print('操作净现金头寸:', cash_end_deal - cash_end_notdeal)
                print('操作净收益:',pv_end_deal+cash_end_deal-pv_end_notdeal-cash_end_notdeal)
            result={}
            result['enddate']=hdp.date
            result['pv_begin'] =pv_begin
            result['cashflow_his_deal'] =cashflow_his_deal
            result['cash_end_deal'] =cash_end_deal
            result['cashflow_for_deal'] =cashflow_for_deal
            result['pv_end_deal'] =pv_end_deal
            result['cashflow_his_notdeal'] =cashflow_his_notdeal
            result['cash_end_notdeal'] =cash_end_notdeal
            result['cashflow_for_notdeal'] =cashflow_for_notdeal
            result['pv_end_notdeal'] =pv_end_notdeal
            resultall.append(result)

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
            if m.facevalue != 0 and (m.enddate - lastdate).days > 0:
                print(m.code, m.facevalue)
        return resultall
    def bsforcast_plot(self,num=1000):

        result=self.bsforcast_tpl()[-1]
        deal_profit=[]
        notdeal_profit=[]
        for i in tqdm(range(0, num)):

            resultx=self.bsforcast_tpl(1)[-1]
            deal_profit.append(resultx['cash_end_deal']+resultx['pv_end_deal']-resultx['pv_begin'])
            notdeal_profit.append(resultx['cash_end_notdeal']+resultx['pv_end_notdeal']-resultx['pv_begin'])

        plt.hist(deal_profit, histtype='stepfilled', alpha=0.3, density=1,
                 bins=200)
        plt.hist(notdeal_profit, histtype='stepfilled', alpha=0.3, density=1,
                 bins=200)
        plt.show()

        return result

    def bsforcast_oci(self,choice=None):
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
            pv_begin += asset.pv()[0]

        for hdp in self.hdp:
            cashflow_for_deal = {}
            cashflow_for_notdeal = {}

            newdate = hdp.date
            if choice:
                newcurve = hdp.curvemo()
            else:
                newcurve = hdp.curve_mu
            pv_final = 0

            interestgain_deal_div=0
            floatinggain_deal = 0
            floatinggain_notdeal = 0
            interestgain_notdeal = 0
            dontlist=[]
            for asset, asset0 in zip(self.asset_deal, self.asset_notdeal):
                # 计算交易操作的结果（deal）
                if asset.code in hdp.buysell.keys():

                    if hdp.buysell[asset.code]>0:

                        assetlist=[]
                        for name in self.asset_deal:
                            assetlist.append(name.code)
                        k=0
                        while True:
                            k += 1
                            code = asset.code + '-' + str(k)

                            if code not in assetlist:
                                break


                        ctype =asset.ctype
                        initialdate = asset.initialdate
                        enddate = asset.enddate
                        facevalue = hdp.buysell[asset.code]
                        couponrate =asset.couponrate
                        assementdate = hdp.date
                        curve =hdp.curve_mu
                        frequency = asset.frequency
                        assetappend=FXIncome.asset_bond(code, ctype, initialdate, enddate, facevalue, couponrate, assementdate, curve, frequency)
                        assetappend.cleanprice_fill()

                        self.asset_deal.append(assetappend)

                        asset_pv1 = assetappend.pv(facetype=1)[0]
                        cash = -asset_pv1 * hdp.buysell[asset.code]
                        asset_cashflow0 = assetappend.cashflow()


                        facevalue=0
                        assetappend2=FXIncome.asset_bond(code, ctype, initialdate, enddate, facevalue, couponrate, assementdate, curve, frequency)
                        assetappend2.cleanprice_fill()
                        self.asset_notdeal.append(assetappend2)


                        asset.change(newdate=newdate, newcurve=newcurve)

                        cleanprice_market1 = asset.cleanprice_func()
                        cleanprice_def1 = asset.cleanprice_interestgain()[0]
                        floatinggain_deal += (cleanprice_market1 - cleanprice_def1)

                        interestgain_deal += asset.cleanprice_interestgain()[1]
                        interestgain_deal_div += asset.cleanprice_interestgain()[1]

                        pv_final += asset.pv()[0]
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
                        sellvol=hdp.buysell[asset.code]
                        asset_in=asset
                        k = 0

                        while sellvol<0:
                            if sellvol+asset_in.facevalue<=0:
                                sellvol_in=-asset_in.facevalue
                                sellvol-=sellvol_in
                            else:
                                sellvol_in=sellvol
                                sellvol=0


                            asset_cashflow0 = asset_in.cashflow()
                            asset_in.change(newdate=newdate, newcurve=newcurve)
                            asset_pv1 = asset_in.pv(facetype=1)[0]
                            cash = -asset_pv1 * sellvol_in

                            cleanprice_market0=asset_in.cleanprice_func()
                            cleanprice_def0=asset_in.cleanprice_interestgain()[0]
                            interestgain_deal+=asset_in.cleanprice_interestgain()[1]


                            asset_in.change(facevaluedelta=sellvol_in)

                            cleanprice_market1 = asset_in.cleanprice_func()
                            cleanprice_def1 = asset_in.cleanprice_interestgain()[0]
                            interestgain_deal_div += asset_in.cleanprice_interestgain()[1]
                            pricegain=(cleanprice_market0-cleanprice_def0)-(cleanprice_market1-cleanprice_def1)
                            pricegain_deal+=pricegain
                            floatinggain_deal+=(cleanprice_market1-cleanprice_def1)
                            if sellvol!=0:
                                k +=1
                                code = asset_in.code + '-' + str(k)
                                for mmm in self.asset_deal:
                                    if code==mmm.code:
                                        asset_in=mmm
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
                    asset_cashflow0 = asset.cashflow()
                    for i, j in asset_cashflow0.items():
                        if (i - hdp.date).days <= 0:
                            if i in cashflow_his_deal.keys():
                                cashflow_his_deal[i] += j
                            else:
                                cashflow_his_deal[i] = j
                    asset.change(newdate=newdate, newcurve=newcurve)

                    cleanprice_market1 = asset.cleanprice_func()
                    cleanprice_def1 = asset.cleanprice_interestgain()[0]
                    floatinggain_deal += (cleanprice_market1 - cleanprice_def1)

                    interestgain_deal += asset.cleanprice_interestgain()[1]
                    interestgain_deal_div += asset.cleanprice_interestgain()[1]


                    pv_final += asset.pv()[0]


                for i, j in asset.pv()[1].items():
                    if i != asset.assementdate:
                        if i in cashflow_for_deal:
                            cashflow_for_deal[i] += j
                        else:
                            cashflow_for_deal[i] = j
                # 计算不交易操作的结果（notdeal）
                asset_cashflow0 = asset0.cashflow()
                for i, j in asset_cashflow0.items():
                    if (i - newdate).days <= 0:
                        if i in cashflow_his_notdeal.keys():
                            cashflow_his_notdeal[i] += j
                        else:
                            cashflow_his_notdeal[i] = j
                asset0.change(newdate=newdate, newcurve=newcurve)
                asset_cashflow1 = asset0.pv()[1]
                for i, j in asset_cashflow1.items():
                    if i != asset.assementdate:
                        if i in cashflow_for_notdeal.keys():
                            cashflow_for_notdeal[i] += j
                        else:
                            cashflow_for_notdeal[i] = j
                cleanprice_market1 = asset0.cleanprice_func()
                cleanprice_def1 = asset0.cleanprice_interestgain()[0]
                interestgain_notdeal += asset0.cleanprice_interestgain()[1]

                floatinggain_notdeal += cleanprice_market1 - cleanprice_def1

                pv_end_notdeal += asset0.pv()[0]

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
                print('价差收益',pricegain_deal)
                print('浮动盈亏',floatinggain_deal)
                print('利息收益',interestgain_deal)
                print('损益总计',pricegain_deal+floatinggain_deal+interestgain_deal)
                print('-------------2不操作------------')
                print('结束日已获得现金流:', cashflow_his_notdeal)
                print('结束日现金头寸:', cash_end_notdeal)
                print('结束日未来折现现金流:', cashflow_for_notdeal)
                print('结束日债券价值:', pv_end_notdeal)
                print('价差收益', pricegain_notdeal)
                print('浮动盈亏', floatinggain_notdeal)
                print('利息收益', interestgain_notdeal)
                print('损益总计',pricegain_notdeal+floatinggain_notdeal+interestgain_notdeal)
                print('-------------3对比------------')
                print('操作净现金头寸:', cash_end_deal - cash_end_notdeal)
                print('操作净价差收益:',pricegain_deal-pricegain_notdeal)
                print('操作净浮动盈亏:',floatinggain_deal-floatinggain_notdeal)
                print('操作净利息收益:',interestgain_deal-interestgain_notdeal)
                print('操作净损益总计',pricegain_deal+floatinggain_deal+interestgain_deal-(pricegain_notdeal+floatinggain_notdeal+interestgain_notdeal))
            result = {}
            result['enddate'] = hdp.date
            result['pv_begin'] = pv_begin
            result['cashflow_his_deal'] = cashflow_his_deal
            result['cash_end_deal'] = cash_end_deal
            result['cashflow_for_deal'] = cashflow_for_deal
            result['pv_end_deal'] = pv_end_deal

            result['pricegain_deal']=pricegain_deal
            result['floatinggain_deal']=floatinggain_deal
            result['interestgain_deal']=interestgain_deal



            result['cashflow_his_notdeal'] = cashflow_his_notdeal
            result['cash_end_notdeal'] = cash_end_notdeal
            result['cashflow_for_notdeal'] = cashflow_for_notdeal
            result['pv_end_notdeal'] = pv_end_notdeal

            result['pricegain_notdeal'] = pricegain_notdeal
            result['floatinggain_notdeal'] = floatinggain_notdeal
            result['interestgain_notdeal'] = interestgain_notdeal

            resultall.append(result)
            interestgain_deal-=interestgain_deal_div

        print('--------------------最终日核算---------------')
        print('-------------1操作历史累计现金头寸------------')
        jj = 0
        cashflow_his_deal_list=sorted(cashflow_his_deal.keys())
        for i in cashflow_his_deal_list:
            if cashflow_his_deal[i]!=0:
                jj+=cashflow_his_deal[i]
                print(i,jj)

        print('-------------2不操作历史累计现金头寸------------')
        jj = 0
        cashflow_his_notdeal_list = sorted(cashflow_his_notdeal.keys())
        for i in cashflow_his_notdeal_list:
            if cashflow_his_notdeal[i] != 0:
                jj += cashflow_his_notdeal[i]
                print(i, jj)
        print('-------------3操作后最终债券剩余面额------------')

        lastdate=hdp.date
        for m in self.asset_deal:
            if m.facevalue!=0 and (m.enddate-lastdate).days>0:
                print(m.code,m.facevalue)
        return resultall
    def stresstest(self):
        pass