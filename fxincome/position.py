import datetime
from dateutil.relativedelta import relativedelta



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

class PositionBond(Position):

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
