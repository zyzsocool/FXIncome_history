# coding=utf-8
import datetime
from dateutil.relativedelta import relativedelta
from fxincome.const import COUPON_TYPE


class Asset:
    """
    Args:
        code(str): ID of the asset
        ctype(Enum): 付息或贴息
        initial_date(datetime):起息日
        end_date(datetime):到期日
        coupon_rate(float):票面利息
    """

    def __init__(self, code, ctype, initial_date, end_date, coupon_rate):
        self.code = code
        self.ctype = ctype
        self.initial_date = initial_date
        self.end_date = end_date
        # self.face_value = face_value
        self.coupon_rate = coupon_rate
        # self.assessment_date = assessment_date
        # self.curve = curve

    def cashflow(self, assessment_date):
        pass

    def pv(self, assessment_date, curve, ytm_change=0):
        pass

    def dv01(self, assessment_date, curve):
        pass

    # def change(self, newdate=None, newcurve=None, face_value_delta=None):
    #     if newdate:
    #         self.assessment_date = newdate
    #     if newcurve:
    #         self.curve = newcurve
    #     if face_value_delta:
    #         self.face_value += face_value_delta


class Bond(Asset):
    """
    Args:
        frequency(int):付息频率，每年X次
    """

    def __init__(self, code, ctype, initial_date, end_date, coupon_rate, frequency):
        super().__init__(code, ctype, initial_date, end_date, coupon_rate)
        self.frequency = frequency

    def ytm(self, assessment_date, curve):
        """

        Args:
            assessment_date(datetime):评估日
            curve(dict):收益率曲线，Key关键期限包括 0，3M,6M, 9M, 1Y, 2Y, 3Y, 5Y, 10Y, 20Y, 30Y
                                  Value是对应的收益率， float
        Returns:
            插值后的收益率，float
        """
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

    def cashflow(self, assessment_date):
        face_value = 1
        cash_flow = {}
        if self.ctype == COUPON_TYPE.REGULAR:
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
        elif self.ctype == COUPON_TYPE.ZERO:
            cash_flow[self.end_date] = face_value
        return cash_flow

    def pv(self, assessment_date, curve, ytm_change=0):
        cash_flow = self.cashflow(assessment_date)
        if self.ctype == COUPON_TYPE.REGULAR:
            ytm = (self.ytm(assessment_date, curve) + ytm_change) / self.frequency
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

    def cleanprice_func(self, assessment_date, curve):

        facevalue = 1
        if self.ctype == COUPON_TYPE.REGULAR:
            pv = self.pv(assessment_date, curve)[0]
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

    def dv01(self, assessment_date, curve):
        pvdown = self.pv(assessment_date, curve, -0.00005)[0]

        pvup = self.pv(assessment_date, curve, 0.00005)[0]
        return pvup - pvdown


class IRS(Asset):
    def __init__(self, code, ctype, initial_date, end_date, face_value, coupon_rate, assement_date, curve):
        super().__init__(code, ctype, initial_date, end_date, face_value, coupon_rate, assement_date, curve)
