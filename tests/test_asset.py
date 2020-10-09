from fxincome import Bond
from fxincome.const import COUPON_TYPE
import pytest
from datetime import datetime


class TestBond:

    @pytest.fixture(scope='class')
    def my_bond(self):
        # 110015 is a 10 years treasure with 2 times payment per year.
        bond = Bond(code='209901',
                    ctype=COUPON_TYPE.ZERO,
                    initial_date=datetime(2020, 1, 6),
                    end_date=datetime(2020, 4, 6),
                    coupon_rate=0.018911,
                    frequency=0
                    )
        return bond

    def test_ytm(self, my_bond):
        bond = my_bond
        assess_date = datetime(2020, 1, 10)
        curve = {
            '0': 0.015,
            '3M': 0.015,
            '6M': 0.015,
            '9M': 0.015,
            '1Y': 0.015,
            '2Y': 0.015,
            '3Y': 0.015,
            '4Y': 0.015,
            '5Y': 0.015,
            '10Y': 0.015,
            '20Y': 0.015,
            '30Y': 0.015}
        assert bond.ytm(assess_date,curve) == 0.015

    def test_cashflow(self, my_bond):
        bond = my_bond
        assess_date = datetime(2020, 1, 10)
        cf = {datetime(2020, 4, 6):1}
        assert bond.cashflow(assess_date) == cf

    def test_pv(self,my_bond):
        bond = my_bond
        assess_date = datetime(2020, 1, 10)
        curve = {
            '0': 0.015,
            '3M': 0.015,
            '6M': 0.015,
            '9M': 0.015,
            '1Y': 0.015,
            '2Y': 0.015,
            '3Y': 0.015,
            '4Y': 0.015,
            '5Y': 0.015,
            '10Y': 0.015,
            '20Y': 0.015,
            '30Y': 0.015}
        assert round(bond.pv(assess_date,curve)[0],6)==0.996447

    def test_pv_cleanprice(self,my_bond):
        bond = my_bond
        assess_date = datetime(2020, 1, 10)
        curve = {
            '0': 0.015,
            '3M': 0.015,
            '6M': 0.015,
            '9M': 0.015,
            '1Y': 0.015,
            '2Y': 0.015,
            '3Y': 0.015,
            '4Y': 0.015,
            '5Y': 0.015,
            '10Y': 0.015,
            '20Y': 0.015,
            '30Y': 0.015}
        assert round(bond.pv_cleanprice(assess_date,curve),6)==0.996241

    def test_dv01(self,my_bond):
        bond = my_bond
        assess_date = datetime(2020, 1, 10)
        curve = {
            '0': 0.015,
            '3M': 0.015,
            '6M': 0.015,
            '9M': 0.015,
            '1Y': 0.015,
            '2Y': 0.015,
            '3Y': 0.015,
            '4Y': 0.015,
            '5Y': 0.015,
            '10Y': 0.015,
            '20Y': 0.015,
            '30Y': 0.015}
        assert round(bond.dv01(assess_date,curve)*100,4)==-0.0024

