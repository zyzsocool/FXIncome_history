import datetime
from dateutil.relativedelta import relativedelta


class Asset:
    def __init__(self, code, ctype, initial_date, end_date, face_value, coupon_rate, assement_date, curve):
        self.code = code
        self.ctype = ctype
        self.initial_date = initial_date
        self.end_date = end_date
        self.face_value = face_value
        self.coupon_rate = coupon_rate
        self.assement_date = assement_date
        self.curve = curve

    def cashflow(self):
        pass

    def pv(self, ytm_change=0):
        pass

    def dv01(self):
        pass

    def change(self, newdate=None, newcurve=None, face_value_delta=None):
        if newdate:
            self.assement_date = newdate
        if newcurve:
            self.curve = newcurve
        if face_value_delta:
            self.face_value += face_value_delta


class Bond(Asset):
    def __init__(self, code, ctype, initial_date, end_date, face_value, coupon_rate, assement_date, curve, frequency,
                 cleanprice=None):
        super().__init__(code, ctype, initial_date, end_date, face_value, coupon_rate, assement_date, curve)
        self.frequency = frequency
        self.cleanprice = cleanprice
        self.realR = None
        self.initial_assementdate = assement_date

    def ytm(self):
        maturity = (self.end_date - self.assement_date).days
        if maturity < 0:
            ytm = self.curve['0']
        elif maturity < 91:
            ytm = self.curve['0'] + (self.curve['3M'] - self.curve['0']) / 91 * maturity
        elif maturity < 182:
            ytm = self.curve['3M'] + (self.curve['6M'] - self.curve['3M']) / (182 - 91) * (maturity - 91)
        elif maturity < 273:
            ytm = self.curve['6M'] + (self.curve['9M'] - self.curve['6M']) / (273 - 182) * (maturity - 182)
        elif maturity < 365:
            ytm = self.curve['9M'] + (self.curve['1Y'] - self.curve['9M']) / (365 - 273) * (maturity - 273)
        elif maturity < 365 * 2:
            ytm = self.curve['1Y'] + (self.curve['2Y'] - self.curve['1Y']) / 365 * (maturity - 365)
        elif maturity < 365 * 3:
            ytm = self.curve['2Y'] + (self.curve['3Y'] - self.curve['2Y']) / 365 * (maturity - 365 * 2)
        elif maturity < 365 * 4:
            ytm = self.curve['3Y'] + (self.curve['4Y'] - self.curve['3Y']) / 365 * (maturity - 365 * 3)
        elif maturity < 365 * 5:
            ytm = self.curve['4Y'] + (self.curve['5Y'] - self.curve['4Y']) / 365 * (maturity - 365 * 4)
        elif maturity < 365 * 10:
            ytm = self.curve['5Y'] + (self.curve['10Y'] - self.curve['5Y']) / 365 / 5 * (maturity - 365 * 5)
        elif maturity < 365 * 20:
            ytm = self.curve['10Y'] + (self.curve['20Y'] - self.curve['10Y']) / 365 / 10 * (maturity - 365 * 10)
        elif maturity < 365 * 30:
            ytm = self.curve['20Y'] + (self.curve['30Y'] - self.curve['20Y']) / 365 / 10 * (maturity - 365 * 20)
        else:
            ytm = None
        return ytm

    def cashflow(self):
        face_value = 1
        cash_flow = {}
        if self.ctype == '附息':
            date = self.initial_date
            coupon = self.coupon_rate / self.frequency * face_value
            period = 12 / self.frequency
            while (date - self.end_date).days < 10:
                if (date - self.assement_date).days >= 0:
                    cash_flow[date] = coupon
                date += relativedelta(months=period)
            date -= relativedelta(months=period)
            if cash_flow:
                cash_flow[date] += face_value
        elif self.ctype == '贴现':
            cash_flow[self.end_date] = face_value
        return cash_flow
    def pv(self, ytm_change=0):
        cash_flow = self.cashflow()
        if self.ctype == '附息':
            ytm = (self.ytm() + ytm_change) / self.frequency
            cash_flow_deflated = {}

            pv = 0
            if cash_flow:
                firstdate = min(cash_flow.keys())
                period = 12 / self.frequency
                lastdate = firstdate - relativedelta(months=period)
                days = (firstdate - self.assement_date).days / (firstdate - lastdate).days
                maxday = (max(cash_flow.keys()) - self.assement_date).days

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
    def cleanprice_func(self):

        facevalue = 1
        if self.ctype == '附息':
            pv = self.pv()[0]
            datelist = sorted(self.cashflow().keys())
            if datelist:

                firstdate = datelist[0]
                period = 12 / self.frequency
                lastdate = firstdate - relativedelta(months=period)
                dayall = (firstdate - lastdate).days
                daycount = (self.assement_date - lastdate).days
                interest = daycount / dayall * self.coupon_rate / self.frequency
                cleanprice = pv - interest * facevalue
            else:
                cleanprice = 0
        return cleanprice

    def dv01(self):
        pvdown = self.pv(-0.00005)[0]

        pvup = self.pv(0.00005)[0]
        return pvup - pvdown

    def realdailyR(self):
        if self.ctype == '附息':
            datelist = sorted(self.cashflow().keys())

            firstdate = datelist[0]
            period = 12 / self.frequency
            lastdate = firstdate - relativedelta(months=period)
            datelist.insert(0, lastdate)

            realR_up = 0.2 / 365
            realR_down = 0

            while True:
                date = self.initial_assementdate
                cleanprice = self.cleanprice
                realR = (realR_up + realR_down) / 2
                i = 1
                yearday = (datelist[1] - datelist[0]).days
                while (date - datelist[-1]).days < 0:
                    if (date - datelist[i]).days >= 0:
                        yearday = (datelist[i + 1] - datelist[i]).days
                        i += 1

                    cleanprice = cleanprice * (1 + realR) - self.coupon_rate / yearday * 100 / self.frequency

                    date += relativedelta(days=1)

                if cleanprice - 100 > 0:
                    realR_up = realR
                else:
                    realR_down = realR

                if abs(cleanprice - 100) < 0.000000001:
                    break

        self.realR = realR
        return realR

    def cleanprice_interestgain(self):  # 算的是当天日初折溢摊净价，也是昨日日终折溢摊净价

        if self.realR:
            realR = self.realR
        else:
            realR = self.realdailyR()

        if self.ctype == '附息':

            assementdate = self.assement_date
            date = self.initial_assementdate
            self.change(newdate=date)

            datelist = sorted(self.cashflow().keys())
            self.change(newdate=assementdate)
            firstdate = datelist[0]
            period = 12 / self.frequency
            lastdate = firstdate - relativedelta(months=period)
            datelist.insert(0, lastdate)

            assementdate = self.assement_date
            date = self.initial_assementdate
            cleanprice = self.cleanprice
            yearday = (datelist[1] - datelist[0]).days
            i = 1
            interestgain = 0
            while (assementdate - date).days > 0 and (self.end_date - date).days > 0:
                if (date - datelist[i]).days == 0:
                    yearday = (datelist[i + 1] - datelist[i]).days
                    i += 1
                interestgain += cleanprice * realR
                cleanprice = cleanprice * (1 + realR) - self.coupon_rate / self.frequency / yearday * 100
                date += relativedelta(days=1)

        if (assementdate - self.end_date).days > 0:
            cleanprice = 0

        cleanprice = cleanprice / 100
        interestgain = interestgain / 100



        return [cleanprice, interestgain]




    def cleanprice_fill(self):
        cleanprice = self.cleanprice_func() * 100
        self.cleanprice = cleanprice



    #带individual的都是考虑资产名义本金的，不带的名义本金就是1
    def cashflow_individual(self):
        face_value = self.face_value
        cash_flow = {}
        if self.ctype == '附息':
            date = self.initial_date
            coupon = self.coupon_rate / self.frequency * face_value
            period = 12 / self.frequency
            while (date - self.end_date).days < 10:
                if (date - self.assement_date).days >= 0:
                    cash_flow[date] = coupon
                date += relativedelta(months=period)
            date -= relativedelta(months=period)
            if cash_flow:
                cash_flow[date] += face_value
        elif self.ctype == '贴现':
            cash_flow[self.end_date] = face_value
        return cash_flow
    def cleanprice_func_individual(self):

        facevalue = self.face_value
        if self.ctype == '附息':
            pv = self.pv_individual()[0]
            datelist = sorted(self.cashflow().keys())
            if datelist:

                firstdate = datelist[0]
                period = 12 / self.frequency
                lastdate = firstdate - relativedelta(months=period)
                dayall = (firstdate - lastdate).days
                daycount = (self.assement_date - lastdate).days
                interest = daycount / dayall * self.coupon_rate / self.frequency
                cleanprice = pv - interest * facevalue
            else:
                cleanprice = 0
        return cleanprice
    def pv_individual(self, ytm_change=0):

        cash_flow = self.cashflow_individual()
        if self.ctype == '附息':
            ytm = (self.ytm() + ytm_change) / self.frequency
            cash_flow_deflated = {}

            pv = 0
            if cash_flow:
                firstdate = min(cash_flow.keys())
                period = 12 / self.frequency
                lastdate = firstdate - relativedelta(months=period)
                days = (firstdate - self.assement_date).days / (firstdate - lastdate).days
                maxday = (max(cash_flow.keys()) - self.assement_date).days

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
    def cleanprice_interestgain_individual(self):  # 算的是当天日初折溢摊净价，也是昨日日终折溢摊净价

        if self.realR:
            realR = self.realR
        else:
            realR = self.realdailyR()

        if self.ctype == '附息':

            assementdate = self.assement_date
            date = self.initial_assementdate
            self.change(newdate=date)

            datelist = sorted(self.cashflow().keys())
            self.change(newdate=assementdate)
            firstdate = datelist[0]
            period = 12 / self.frequency
            lastdate = firstdate - relativedelta(months=period)
            datelist.insert(0, lastdate)

            assementdate = self.assement_date
            date = self.initial_assementdate
            cleanprice = self.cleanprice
            yearday = (datelist[1] - datelist[0]).days
            i = 1
            interestgain = 0
            while (assementdate - date).days > 0 and (self.end_date - date).days > 0:
                if (date - datelist[i]).days == 0:
                    yearday = (datelist[i + 1] - datelist[i]).days
                    i += 1
                interestgain += cleanprice * realR
                cleanprice = cleanprice * (1 + realR) - self.coupon_rate / self.frequency / yearday * 100
                date += relativedelta(days=1)

        if (assementdate - self.end_date).days > 0:
            cleanprice = 0



        cleanprice = cleanprice * self.face_value / 100
        interestgain = interestgain * self.face_value / 100

        return [cleanprice, interestgain]
    def dv01_individual(self):
        pvdown = self.pv_individual(-0.00005)[0]

        pvup = self.pv_individual(0.00005)[0]
        return pvup - pvdown


class IRS(Asset):
    def __init__(self, code, ctype, initial_date, end_date, face_value, coupon_rate, assement_date, curve):
        super().__init__(code, ctype, initial_date, end_date, face_value, coupon_rate, assement_date, curve)
