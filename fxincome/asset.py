import datetime
from dateutil.relativedelta import relativedelta


class Asset:
    def __init__(self, code, ctype, initial_date, end_date, coupon_rate):
        self.code = code
        self.ctype = ctype
        self.initial_date = initial_date
        self.end_date = end_date
        #self.face_value = face_value
        self.coupon_rate = coupon_rate
        #self.assessment_date = assessment_date
        #self.curve = curve

    def cashflow(self,assessment_date):
        pass

    def pv(self,assessment_date,curve, ytm_change=0):
        pass

    def dv01(self,assessment_date,curve):
        pass

    def change(self, newdate=None, newcurve=None, face_value_delta=None):
        if newdate:
            self.assessment_date = newdate
        if newcurve:
            self.curve = newcurve
        if face_value_delta:
            self.face_value += face_value_delta


class Bond(Asset):
    def __init__(self, code, ctype, initial_date, end_date, coupon_rate, frequency):
        super().__init__(code, ctype, initial_date, end_date, coupon_rate)
        self.frequency = frequency
        self.realR = None


    def ytm(self,assessment_date,curve):
        maturity = (self.end_date - assessment_date).days
        if maturity < 0:
            ytm = curve['0']
        elif maturity < 91:
            ytm = curve['0'] + (curve['3M'] - curve['0']) / 91 * maturity
        elif maturity < 182:
            ytm = curve['3M'] + (curve['6M'] - curve['3M']) / (182 - 91) * (maturity - 91)
        elif maturity < 273:
            ytm = curve['6M'] + (curve['9M'] - curve['6M']) / (273 - 182) * (maturity - 182)
        elif maturity < 365:
            ytm = curve['9M'] + (curve['1Y'] - curve['9M']) / (365 - 273) * (maturity - 273)
        elif maturity < 365 * 2:
            ytm = curve['1Y'] + (curve['2Y'] - curve['1Y']) / 365 * (maturity - 365)
        elif maturity < 365 * 3:
            ytm = curve['2Y'] + (curve['3Y'] - curve['2Y']) / 365 * (maturity - 365 * 2)
        elif maturity < 365 * 4:
            ytm = curve['3Y'] + (curve['4Y'] - curve['3Y']) / 365 * (maturity - 365 * 3)
        elif maturity < 365 * 5:
            ytm = curve['4Y'] + (curve['5Y'] - curve['4Y']) / 365 * (maturity - 365 * 4)
        elif maturity < 365 * 10:
            ytm = curve['5Y'] + (curve['10Y'] - curve['5Y']) / 365 / 5 * (maturity - 365 * 5)
        elif maturity < 365 * 20:
            ytm = curve['10Y'] + (curve['20Y'] - curve['10Y']) / 365 / 10 * (maturity - 365 * 10)
        elif maturity < 365 * 30:
            ytm = curve['20Y'] + (curve['30Y'] - curve['20Y']) / 365 / 10 * (maturity - 365 * 20)
        else:
            ytm = None
        return ytm
    def cashflow(self,assessment_date):
        face_value = 1
        cash_flow = {}
        if self.ctype == '附息':
            date = self.initial_date
            coupon = self.coupon_rate / self.frequency * face_value
            period = 12 / self.frequency
            while (date - self.end_date).days < 10:
                if (date - assessment_date).days >= 0:
                    cash_flow[date] = coupon
                date += relativedelta(months=period)
            date -= relativedelta(months=period)
            if cash_flow:
                cash_flow[date] += face_value
        elif self.ctype == '贴现':
            cash_flow[self.end_date] = face_value
        return cash_flow
    def pv(self,assessment_date,curve, ytm_change=0):
        cash_flow = self.cashflow(assessment_date)
        if self.ctype == '附息':
            ytm = (self.ytm(assessment_date,curve) + ytm_change) / self.frequency
            cash_flow_deflated = {}

            pv = 0
            if cash_flow:
                firstdate = min(cash_flow.keys())
                period = 12 / self.frequency
                lastdate = firstdate - relativedelta(months=period)
                days = (firstdate - assessment_date).days / (firstdate - lastdate).days
                maxday = (max(cash_flow.keys()) - assessment_date).days

                if maxday >= 365:
                    for i, j in cash_flow.items():
                        value = j / (1 + ytm) ** days
                        cash_flow_deflated[i] = value
                        pv += value
                        days += 1
                else:
                    for i, j in cash_flow.items():
                        value = j / (1 + ytm * days)
                        cash_flow_deflated[i] = value
                        pv += value
                        days += 1

        return [pv, cash_flow_deflated]
    def cleanprice_func(self,assessment_date,curve):

        facevalue = 1
        if self.ctype == '附息':
            pv = self.pv(assessment_date,curve)[0]
            datelist = sorted(self.cashflow(assessment_date).keys())
            if datelist:

                firstdate = datelist[0]
                period = 12 / self.frequency
                lastdate = firstdate - relativedelta(months=period)
                dayall = (firstdate - lastdate).days
                daycount = (assessment_date - lastdate).days
                interest = daycount / dayall * self.coupon_rate / self.frequency
                cleanprice = pv - interest * facevalue
            else:
                cleanprice = 0
        return cleanprice
    def dv01(self,assessment_date,curve):
        pvdown = self.pv(assessment_date,curve,-0.00005)[0]

        pvup = self.pv(assessment_date,curve,0.00005)[0]
        return pvup - pvdown


class IRS(Asset):
    def __init__(self, code, ctype, initial_date, end_date, face_value, coupon_rate, assement_date, curve):
        super().__init__(code, ctype, initial_date, end_date, face_value, coupon_rate, assement_date, curve)




class Position():
    def __init__(self, asset, face_value, assessment_date, curve):
        self.asset = asset
        self.face_value = face_value
        self.assessment_date = assessment_date
        self.initial_assessment_date = assessment_date
        self.curve = curve
    def change(self, newdate=None, newcurve=None, face_value_delta=None):
        if newdate:
            self.assessment_date = newdate
        if newcurve:
            self.curve = newcurve
        if face_value_delta:
            self.face_value += face_value_delta
    def cashflow(self):
        pass
    def pv(self):
        pass
    def dv01(self):
        pass

class Position_Bond(Position):

    def __init__(self, asset, face_value, assessment_date, curve,cleanprice=None):
        super().__init__(asset, face_value, assessment_date, curve)

        self.cleanprice=self.asset.cleanprice_func(self.assessment_date,self.curve) * 100 if not cleanprice else cleanprice
        self.realR = self.realdailyR()
        self.initial_assessment_date = assessment_date
    def cashflow(self):
        cashflow=self.asset.cashflow(self.assessment_date)
        for date,flow in cashflow.items():
            cashflow[date]=flow*self.face_value
        return cashflow
    def pv(self, ytm_change=0):
        [pv, cash_flow_deflated]=self.asset.pv(self.assessment_date,self.curve, ytm_change)
        pv=pv*self.face_value
        for date,flow in cash_flow_deflated.items():
            cash_flow_deflated[date]=flow*self.face_value
        return [pv, cash_flow_deflated]
    def dv01(self):
        return self.asset.dv01(self.assessment_date,self.curve)*self.face_value
    def realdailyR(self):
        if self.asset.ctype == '附息':
            datelist = sorted(self.cashflow().keys())

            firstdate = datelist[0]
            period = 12 / self.asset.frequency
            lastdate = firstdate - relativedelta(months=period)
            datelist.insert(0, lastdate)

            realR_up = 0.2 / 365
            realR_down = 0

            while True:
                date = self.initial_assessment_date
                cleanprice = self.cleanprice
                realR = (realR_up + realR_down) / 2
                i = 1
                yearday = (datelist[1] - datelist[0]).days
                while (date - datelist[-1]).days < 0:
                    if (date - datelist[i]).days >= 0:
                        yearday = (datelist[i + 1] - datelist[i]).days
                        i += 1

                    cleanprice = cleanprice * (1 + realR) - self.asset.coupon_rate / yearday * 100 / self.asset.frequency

                    date += relativedelta(days=1)

                if cleanprice - 100 > 0:
                    realR_up = realR
                else:
                    realR_down = realR

                if abs(cleanprice - 100) < 0.000000001:
                    break


        return realR
    def cleanprice_interestgain(self):  # 算的是当天日初折溢摊净价，也是昨日日终折溢摊净价

        realR = self.realR
        if self.asset.ctype == '附息':

            assessment_date = self.assessment_date
            date = self.initial_assessment_date
            self.change(newdate=date)

            datelist = sorted(self.cashflow().keys())
            self.change(newdate=assessment_date)
            firstdate = datelist[0]
            period = 12 / self.asset.frequency
            lastdate = firstdate - relativedelta(months=period)
            datelist.insert(0, lastdate)

            assessment_date = self.assessment_date
            date = self.initial_assessment_date
            cleanprice = self.cleanprice
            yearday = (datelist[1] - datelist[0]).days
            i = 1
            interestgain = 0
            while (assessment_date - date).days > 0 and (self.asset.end_date - date).days > 0:
                if (date - datelist[i]).days == 0:
                    yearday = (datelist[i + 1] - datelist[i]).days
                    i += 1
                interestgain += cleanprice * realR
                cleanprice = cleanprice * (1 + realR) - self.asset.coupon_rate / self.asset.frequency / yearday * 100
                date += relativedelta(days=1)

        if (assessment_date - self.asset.end_date).days > 0:
            cleanprice = 0

        cleanprice = cleanprice * self.face_value / 100
        interestgain = interestgain * self.face_value / 100



        return [cleanprice, interestgain]






