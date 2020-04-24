import datetime
from dateutil.relativedelta import relativedelta
class asset():
    def __init__(self, code, ctype, initialdate, enddate, facevalue, couponrate, assementdate, curve):
        self.code=code
        self.ctype=ctype
        self.initialdate=initialdate
        self.enddate=enddate
        self.facevalue=facevalue
        self.couponrate=couponrate
        self.assementdate=assementdate
        self.curve=curve
    def cashflow(self):
        pass
    def pv(self):
        pass
    def dv01(self):
        pass
    def change(self,newdate=None,newcurve=None,facevaluedelta=None):
        if newdate:
            self.assementdate=newdate
        if newcurve:
            self.curve=newcurve
        if facevaluedelta:
            self.facevalue+=facevaluedelta



class asset_bond(asset):
    def __init__(self, code, ctype, initialdate, enddate, facevalue, couponrate, assementdate, curve, frequency):
        super().__init__(code, ctype, initialdate, enddate, facevalue, couponrate, assementdate, curve)
        self.frequency=frequency
    def ytm(self):
        maturity=(self.enddate-self.assementdate).days
        if maturity<0:
            ytm=self.curve['0']
        elif maturity<91:
            ytm=self.curve['0']+(self.curve['3M']-self.curve['0'])/91*maturity
        elif maturity < 182:
            ytm = self.curve['3M'] + (self.curve['6M'] - self.curve['3M']) / (182-91) * (maturity-91)
        elif maturity < 273:
            ytm = self.curve['6M'] + (self.curve['9M'] - self.curve['6M']) / (273-182) * (maturity-182)
        elif maturity < 365:
            ytm = self.curve['9M'] + (self.curve['1Y'] - self.curve['9M']) / (365-273) * (maturity - 273)
        elif maturity < 365*2:
            ytm = self.curve['1Y'] + (self.curve['2Y'] - self.curve['1Y']) / 365 * (maturity - 365)
        elif maturity < 365 * 3:
            ytm = self.curve['2Y'] + (self.curve['3Y'] - self.curve['2Y']) / 365 * (maturity - 365*2)
        elif maturity < 365 * 4:
            ytm = self.curve['3Y'] + (self.curve['4Y'] - self.curve['3Y']) / 365 * (maturity - 365 * 3)
        elif maturity < 365 * 5:
            ytm = self.curve['4Y'] + (self.curve['5Y'] - self.curve['4Y']) / 365 * (maturity - 365 * 4)
        elif maturity < 365 * 10:
            ytm = self.curve['5Y'] + (self.curve['10Y'] - self.curve['5Y']) / 365/5 * (maturity - 365 * 5)
        elif maturity < 365 * 20:
            ytm = self.curve['10Y'] + (self.curve['20Y'] - self.curve['10Y']) / 365 / 10 * (maturity - 365 * 10)
        elif maturity < 365 * 30:
            ytm = self.curve['20Y'] + (self.curve['30Y'] - self.curve['20Y']) / 365 / 10 * (maturity - 365 * 20)
        else:
            ytm=None
        return ytm
    def cashflow(self,facetype=None):
        if facetype:
            facevalue=1
        else:
            facevalue=self.facevalue
        cash_flow={}
        if self.ctype=='附息':
            date=self.initialdate
            coupon=self.couponrate/self.frequency*facevalue
            period=12/self.frequency
            while (date-self.enddate).days<10:
                if (date-self.assementdate).days>=0:
                    cash_flow[date]=coupon
                date+=relativedelta(months=period)
            date -= relativedelta(months=period)
            if cash_flow:
                cash_flow[date] += facevalue
        elif self.ctype=='贴现':
            cash_flow[self.enddate]=facevalue
        return cash_flow
    def pv(self,ytmchange=0,facetype=None):
        if facetype:
            cash_flow=self.cashflow(facetype=1)
        else:
            cash_flow=self.cashflow()
        if self.ctype=='附息':
            ytm=(self.ytm()+ytmchange)/self.frequency
            cash_flow_deflated={}

            pv=0
            if cash_flow:
                firstdate=min(cash_flow.keys())
                period = 12 / self.frequency
                lastdate=firstdate-relativedelta(months=period)
                days=(firstdate-self.assementdate).days/(firstdate-lastdate).days
                maxday=(max(cash_flow.keys())-self.assementdate).days

                if maxday>=365:
                    for i,j in cash_flow.items():
                        value=j / (1 + ytm) ** days
                        cash_flow_deflated[i]=value
                        pv+=value
                        days+=1
                else:
                    for i,j in cash_flow.items():
                        value=j / (1 + ytm*days)
                        cash_flow_deflated[i]=value
                        pv+=value
                        days += 1
        return [pv,cash_flow_deflated]
    def dv01(self):
        pvdown=self.pv(-0.00005)[0]

        pvup=self.pv(0.00005)[0]
        return pvup-pvdown







class asset_irs(asset):
    def __init__(self, code, ctype, initialdate, enddate, facevalue, couponrate, assementdate, curve):
        super().__init__(code, ctype, initialdate, enddate, facevalue, couponrate, assementdate, curve)