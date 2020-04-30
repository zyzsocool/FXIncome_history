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
    def __init__(self, code, ctype, initialdate, enddate, facevalue, couponrate, assementdate, curve, frequency,cleanprice=None):
        super().__init__(code, ctype, initialdate, enddate, facevalue, couponrate, assementdate, curve)
        self.frequency=frequency
        self.cleanprice=cleanprice
        self.realR=None
        self.initial_assementdate=assementdate

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
    def cleanprice_func(self,facetype=None):
        if facetype:
            facevalue=1
        else:
            facevalue=self.facevalue
        if self.ctype == '附息':
            pv=self.pv(facetype=facetype)[0]
            datelist = sorted(self.cashflow().keys())
            if datelist:

                firstdate = datelist[0]
                period = 12 / self.frequency
                lastdate = firstdate - relativedelta(months=period)
                dayall=(firstdate-lastdate).days
                daycount=(self.assementdate-lastdate).days
                interest=daycount/dayall*self.couponrate/self.frequency
                cleanprice=pv-interest*facevalue
            else:
                cleanprice=0
        return cleanprice

    def dv01(self):
        pvdown=self.pv(-0.00005)[0]

        pvup=self.pv(0.00005)[0]
        return pvup-pvdown
    def realdailyR(self):
        if self.ctype == '附息':
            datelist=sorted(self.cashflow().keys())

            firstdate = datelist[0]
            period = 12 / self.frequency
            lastdate = firstdate - relativedelta(months=period)
            datelist.insert(0,lastdate)





            realR_up=0.2/365
            realR_down=0

            while True:
                date = self.initial_assementdate
                cleanprice = self.cleanprice
                realR=(realR_up+realR_down)/2
                i=1
                yearday=(datelist[1]-datelist[0]).days
                while (date-datelist[-1]).days<0:
                    if (date-datelist[i]).days>=0 :
                        yearday=(datelist[i+1]-datelist[i]).days
                        i+=1


                    cleanprice=cleanprice*(1+realR)-self.couponrate/yearday*100

                    date+=relativedelta(days=1)


                if cleanprice-100>0:
                    realR_up=realR
                else:
                    realR_down=realR

                if abs(cleanprice-100)<0.00000000001:
                    break

        self.realR=realR
        return realR
    def cleanprice_interestgain(self, facetype=None):#算的是当天日初折溢摊净价，也是昨日日终折溢摊净价

        if self.realR:
            realR=self.realR
        else:
            realR=self.realdailyR()

        if self.ctype=='附息':

            assementdate = self.assementdate
            date = self.initial_assementdate
            self.change(newdate=date)

            datelist = sorted(self.cashflow().keys())
            self.change(newdate=assementdate)
            firstdate = datelist[0]
            period = 12 / self.frequency
            lastdate = firstdate - relativedelta(months=period)
            datelist.insert(0, lastdate)

            assementdate=self.assementdate
            date=self.initial_assementdate
            cleanprice=self.cleanprice
            yearday=(datelist[1]-datelist[0]).days
            i=1
            interestgain = 0
            while (assementdate-date).days>0 and (self.enddate-date).days>0:
                if (date-datelist[i]).days==0:
                    yearday = (datelist[i+1] - datelist[i]).days
                    i+=1
                interestgain += cleanprice * realR
                cleanprice=cleanprice*(1+realR)-self.couponrate/self.frequency/yearday*100
                date+=relativedelta(days=1)


        if (assementdate-self.enddate).days>0:
            cleanprice=0
        if facetype:
            cleanprice = cleanprice / 100
            interestgain = interestgain / 100

        else:
            cleanprice = cleanprice * self.facevalue / 100
            interestgain = interestgain * self.facevalue / 100


        return [cleanprice,interestgain]
    def cleanprice_fill(self):
        cleanprice=self.cleanprice_func()
        self.cleanprice=cleanprice
















class asset_irs(asset):
    def __init__(self, code, ctype, initialdate, enddate, facevalue, couponrate, assementdate, curve):
        super().__init__(code, ctype, initialdate, enddate, facevalue, couponrate, assementdate, curve)