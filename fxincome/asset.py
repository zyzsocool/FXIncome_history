# coding=utf-8
import datetime
from dateutil.relativedelta import relativedelta
from fxincome.const import COUPON_TYPE


class Asset:
    """
    Args:
        code(str): ID of the asset
        initial_date(datetime):起息日
        end_date(datetime):到期日
        coupon_rate(float):票面利息
    """

    def __init__(self, code, initial_date, end_date, coupon_rate):
        self.code = code
        self.initial_date = initial_date
        self.end_date = end_date
        self.coupon_rate = coupon_rate

    def cashflow(self, assessment_date):
        pass

    def pv(self, assessment_date, curve, ytm_change=0):
        pass

    def dv01(self, assessment_date, curve):
        pass


class Bond(Asset):
    """
    Args:
        ctype(Enum): 付息或贴息
        frequency(int):付息频率，每年X次
    """

    def __init__(self, code, ctype, initial_date, end_date, coupon_rate, frequency):
        super().__init__(code, initial_date, end_date, coupon_rate)
        self.ctype = ctype
        self.frequency = frequency
        # __cashflow_all:字典，该债券对应的所有现金流
        self.__cashflow_all = self.__cashflow()

    def __cashflow(self):
        face_value = 1
        cash_flow_all = {}
        if self.ctype == COUPON_TYPE.REGULAR:
            date = self.initial_date
            coupon = self.coupon_rate / self.frequency * face_value
            period = int(12 / self.frequency)
            date += relativedelta(months=period)
            while (date - self.end_date).days < 10:
                cash_flow_all[date] = coupon
                date += relativedelta(months=period)
            cash_flow_all[self.end_date] += face_value
        elif self.ctype == COUPON_TYPE.ZERO:
            cash_flow_all[self.end_date] = face_value
        else:
            raise NotImplementedError("Unknown COUPON_TYPE")

        return cash_flow_all

    def cashflow(self, assessment_date=None):
        """
        Args:
            assessment_date(datetime):评估日,可为空
        Returns:
            评估日及之后的现金流，字典；如没有评估日则返回Bond对应的所有现金流
        """
        if assessment_date is None:
            return self.__cashflow_all
        cash_flow = {k: v for k, v in self.__cashflow_all.items() if k >= assessment_date}
        return cash_flow

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

    def pv(self, assessment_date, curve, ytm_change=0):
        """
        Args:
            assessment_date(datetime):评估日，可为空
            curve(dict):收益率曲线，Key关键期限包括 0，3M,6M, 9M, 1Y, 2Y, 3Y, 5Y, 10Y, 20Y, 30Y
                                  Value是对应的收益率， float
            ytm_change(float):收益率曲线关键期限平行变化量，0.01代表1%
        Returns:
            tuple (pv, cash_flow_deflated)
            pv(float) - 根据收益率曲线得出的评估日的现值（全价）
            cash_flow_deflated(dict) - 每个现金流的折现值（全价），它们之和等于返回的第一个参数（现值）。
        """
        cash_flow = self.cashflow(assessment_date)
        cash_flow_deflated = {}
        pv = 0
        if self.ctype == COUPON_TYPE.REGULAR:
            if cash_flow:
                ytm = (self.ytm(assessment_date, curve) + ytm_change) / self.frequency
                firstdate = min(cash_flow.keys())
                period = int(12 / self.frequency)
                last_coupon_date = firstdate - relativedelta(months=period)
                days = (firstdate - assessment_date).days / (firstdate - last_coupon_date).days
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
        elif self.ctype == COUPON_TYPE.ZERO:
            if cash_flow:
                maxday = (self.end_date - assessment_date).days
                yearday = ((self.initial_date + relativedelta(years=1)) - self.initial_date).days
                days = maxday / yearday
                ytm = self.ytm(assessment_date, curve) + ytm_change
                if maxday >= 365:
                    value = 1 / (1 + ytm) ** days

                else:
                    value = 1 / (1 + ytm * days)
                cash_flow_deflated[self.end_date] = value
                pv = value
        else:
            raise NotImplementedError("Unknown COUPON_TYPE")
        return pv, cash_flow_deflated

    def pv_cleanprice(self, assessment_date, curve):
        """
        Args:
            assessment_date(datetime):评估日，可为空
            curve(dict):收益率曲线，Key关键期限包括 0，3M,6M, 9M, 1Y, 2Y, 3Y, 5Y, 10Y, 20Y, 30Y
                                  Value是对应的收益率， float
        Returns:
            cleanprice(float):根据收益率曲线得出的评估日的现值（净价）
        """
        facevalue = 1
        pv = self.pv(assessment_date, curve)[0]
        if self.ctype == COUPON_TYPE.REGULAR:
            datelist = sorted(self.cashflow(assessment_date).keys())
            if datelist:
                firstdate = datelist[0]
                period = int(12 / self.frequency)
                last_coupon_date = firstdate - relativedelta(months=period)
                dayall = (firstdate - last_coupon_date).days
                daycount = (assessment_date - last_coupon_date).days
                interest = daycount / dayall * self.coupon_rate / self.frequency
                cleanprice = pv - interest * facevalue
            else:
                cleanprice = 0

        elif self.ctype == COUPON_TYPE.ZERO:
            if assessment_date <= self.end_date:
                daycount = (assessment_date - self.initial_date).days
                yearday = ((self.initial_date + relativedelta(years=1)) - self.initial_date).days
                dayall = (self.end_date - self.initial_date).days

                interest = daycount / dayall * (1 / (1 + yearday / (dayall * self.coupon_rate)))
                cleanprice = pv - interest * facevalue
            else:
                cleanprice = 0
        else:
            raise NotImplementedError("Unknown COUPON_TYPE")
        return cleanprice

    def dv01(self, assessment_date, curve):
        pvdown = self.pv(assessment_date, curve, -0.00005)[0]

        pvup = self.pv(assessment_date, curve, 0.00005)[0]
        return pvup - pvdown
