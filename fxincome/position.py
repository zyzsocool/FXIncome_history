import datetime
import copy
from dateutil.relativedelta import relativedelta
from fxincome.const import COUPON_TYPE
import numpy as np


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

    def __init__(self, asset, face_value, assessment_date, curve, cleanprice=None):
        super().__init__(asset, face_value, assessment_date, curve)

        self.cleanprice = self.asset.pv_cleanprice(self.assessment_date,
                                                   self.curve) * 100 if not cleanprice else cleanprice
        self.realR = self.realdailyR()
        self.initial_assessment_date = assessment_date

    def cashflow(self):
        cashflow = self.asset.cashflow(self.assessment_date)
        for date, flow in cashflow.items():
            cashflow[date] = flow * self.face_value
        return cashflow

    def pv(self, ytm_change=0):
        [pv, cash_flow_deflated] = self.asset.pv(self.assessment_date, self.curve, ytm_change)
        pv = pv * self.face_value
        for date, flow in cash_flow_deflated.items():
            cash_flow_deflated[date] = flow * self.face_value
        return [pv, cash_flow_deflated]

    def dv01(self):
        return self.asset.dv01(self.assessment_date, self.curve) * self.face_value

    def _realdailyR_history(self):  # (这个超级慢的函数已成为历史，用来留着纪念)
        if self.asset.ctype == COUPON_TYPE.REGULAR:
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
                yearday = (datelist[i] - datelist[i - 1]).days
                while date < datelist[-1]:
                    if date >= datelist[i]:
                        yearday = (datelist[i + 1] - datelist[i]).days
                        i += 1
                    cleanprice = cleanprice * (
                                1 + realR) - self.asset.coupon_rate / yearday * 100 / self.asset.frequency
                    date += relativedelta(days=1)
                if cleanprice - 100 > 0:
                    realR_up = realR
                else:
                    realR_down = realR

                if abs(cleanprice - 100) < 0.00000001:
                    break
        elif self.asset.ctype == COUPON_TYPE.ZERO:
            yearday = ((self.asset.initial_date + relativedelta(years=1)) - self.asset.initial_date).days
            dayall = (self.asset.end_date - self.asset.initial_date).days
            interest = (1 / (1 + yearday / (dayall * self.asset.coupon_rate))) / dayall
            realR_up = 0.2 / 365
            realR_down = 0
            while True:
                date = self.initial_assessment_date
                cleanprice = self.cleanprice
                realR = (realR_up + realR_down) / 2
                while date < self.asset.end_date:
                    cleanprice = cleanprice * (1 + realR) - interest
                    date += relativedelta(days=1)
                if cleanprice - 100 > 0:
                    realR_up = realR
                else:
                    realR_down = realR

                if abs(cleanprice - 100) < 0.000000001:
                    break
        return realR

    def _cleanprice_for_realdailyR(self, r, callist):
        Tlist = callist[0]  # 剩余的每个付息日距离到期日的天数
        tlist = callist[1]  # 剩余的每个付息日对的应付息区间的天数
        nlist = callist[2]  # 剩余的每个付息日对的应付息区间剩余天数
        coupon = self.asset.coupon_rate / self.asset.frequency * 100
        cleanprice = self.cleanprice
        interest = np.ones(Tlist.size) * coupon
        price_interest = sum((interest / tlist * ((1 + r) ** nlist - 1) / r) * (1 + r) ** Tlist)
        price_face = cleanprice * (1 + r) ** sum(nlist)
        price = price_face - price_interest
        return price

    def realdailyR(self):
        if self.asset.ctype == COUPON_TYPE.REGULAR:
            datelist = sorted(self.cashflow().keys())
            enddate = datelist[-1]
            lastdate = datelist[0] - relativedelta(months=12 / self.asset.frequency)
            nlistfirst = (datelist[0] - self.initial_assessment_date).days
            datelist.insert(0, lastdate)
            Tlist = []
            tlist = []
            n = 0
            for date in datelist[1:]:
                Tlist.append((enddate - date).days)
                tlist.append((date - datelist[n]).days)
                n += 1
            nlist = copy.deepcopy(tlist)
            nlist[0] = nlistfirst
            Tlist = np.array(Tlist)  # 剩余的每个付息日距离到期日的天数
            tlist = np.array(tlist)  # 剩余的每个付息日对的应付息区间的天数
            nlist = np.array(nlist)  # 剩余的每个付息日对的应付息区间剩余天数
            callist = [Tlist, tlist, nlist]
            r = 0.01 / 365
            while True:
                price = self._cleanprice_for_realdailyR(r, callist) - 100
                price_div_up = self._cleanprice_for_realdailyR(r + 0.00000001, callist)
                price_div_down = self._cleanprice_for_realdailyR(r - 0.00000001, callist)
                price_div = (price_div_up - price_div_down) / 0.00000002
                r = r - price / price_div
                if abs(price) < 0.00000001:
                    break
        elif self.asset.ctype == COUPON_TYPE.ZERO:
            yearday = ((self.asset.initial_date + relativedelta(years=1)) - self.asset.initial_date).days
            dayall = (self.asset.end_date - self.asset.initial_date).days
            interest = (1 / (1 + yearday / (dayall * self.asset.coupon_rate))) / dayall * 100
            daycal = (self.asset.end_date - self.initial_assessment_date).days
            r = 0.01 / 365
            while True:
                price = self.cleanprice * (1 + r) ** daycal - interest * ((1 + r) ** daycal - 1) / r - 100
                price_div_up = self.cleanprice * (1 + (r + 0.00000001)) ** daycal - interest * (
                        (1 + (r + 0.00000001)) ** daycal - 1) / (r + 0.00000001)
                price_div_down = self.cleanprice * (1 + (r - 0.00000001)) ** daycal - interest * (
                        (1 + (r - 0.00000001)) ** daycal - 1) / (r - 0.00000001)
                price_div = (price_div_up - price_div_down) / 0.00000002
                r = r - price / price_div
                if abs(price) < 0.000000001:
                    break

        return r

    def _cleanprice_interestgain_history(self):  # (这个一般慢的函数已成为历史，用来留着纪念)


        realR = self.realR
        assessment_date = self.assessment_date
        if self.asset.ctype == COUPON_TYPE.REGULAR:

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
            while assessment_date > date and self.asset.end_date > date:
                if date == datelist[i]:
                    yearday = (datelist[i + 1] - datelist[i]).days
                    i += 1
                interestgain += cleanprice * realR
                cleanprice = cleanprice * (1 + realR) - self.asset.coupon_rate / self.asset.frequency / yearday * 100
                date += relativedelta(days=1)

        if assessment_date > self.asset.end_date:
            cleanprice = 0

        cleanprice = cleanprice * self.face_value / 100
        interestgain = interestgain * self.face_value / 100

        return [cleanprice, interestgain]

    def cleanprice_interestgain(self): # 算的是当天日初折溢摊净价，也是昨日日终折溢摊净价
        assessment_date = self.assessment_date
        pricechoice = 1
        if assessment_date > self.asset.end_date:
            assessment_date = self.asset.end_date
            pricechoice = 0
        if self.asset.ctype == COUPON_TYPE.REGULAR:

            Tlist = []
            tlist = []
            self.change(newdate=self.initial_assessment_date)
            datelist = sorted(self.cashflow().keys())
            self.change(newdate=assessment_date)
            lastdate = datelist[0] - relativedelta(months=12 / self.asset.frequency)
            nlistfirst = (datelist[0] - self.initial_assessment_date).days
            datelist.insert(0, lastdate)
            n = 0
            for date in datelist[1:]:

                Tlist.append((assessment_date - date).days)
                tlist.append((date - datelist[n]).days)
                n += 1
                if date >= assessment_date:
                    date -= relativedelta(months=12 / self.asset.frequency)
                    break
            Tlist[-1] = 0

            if len(Tlist) == 1:
                nlist = [(assessment_date - self.initial_assessment_date).days]
            else:
                nlist = copy.deepcopy(tlist)
                nlist[0] = nlistfirst
                nlist[-1] = (assessment_date - date).days
            Tlist = np.array(Tlist)
            tlist = np.array(tlist)
            nlist = np.array(nlist)
            callist = [Tlist, tlist, nlist]
            price = self._cleanprice_for_realdailyR(self.realR, callist) / 100
            coupon = self.asset.coupon_rate / self.asset.frequency
            coupon = np.ones(Tlist.size) * coupon
            couponsum = sum(coupon / tlist * nlist)
            interestgain = price - self.cleanprice / 100 + couponsum

        elif self.asset.ctype == COUPON_TYPE.ZERO:
            yearday = ((self.asset.initial_date + relativedelta(years=1)) - self.asset.initial_date).days
            dayall = (self.asset.end_date - self.asset.initial_date).days
            interest = (1 / (1 + yearday / (dayall * self.asset.coupon_rate))) / dayall * 100
            daycal = (assessment_date-self.initial_assessment_date).days
            r = self.realR
            price = (self.cleanprice * (1 + r) ** daycal - interest * ((1 + r) ** daycal - 1) / r) / 100
            interestgain = price - self.cleanprice / 100
        interestgain = interestgain * self.face_value
        price = price * self.face_value*pricechoice
        return [price, interestgain]
