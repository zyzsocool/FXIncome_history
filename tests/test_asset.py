from fxincome import Bond
from fxincome.const import COUPON_TYPE
import pytest
from datetime import datetime


class TestBond:

    @pytest.fixture(scope='class')
    def my_bond(self):
        # 110015 is a 10 years treasure with 2 times payment per year.
        bond = Bond(code='110015',
                    ctype=COUPON_TYPE.REGULAR,
                    initial_date=datetime(2011, 6, 16),
                    end_date=datetime(2021, 6, 16),
                    coupon_rate=0.0399,
                    frequency=2
                    )
        return bond

    def test_ytm(self):
        assert False

    def test_cashflow(self, my_bond):
        bond = my_bond
        assess_date = datetime(2020, 9, 20)
        cf = {datetime(2020, 12, 16):0.0399/2,
              datetime(2021, 6, 16):(1 + 0.0399/2)}
        assert bond.cashflow(assess_date) == cf

    def test_pv(self):
        assert False

    def test_cleanprice_func(self):
        assert False

    def test_dv01(self):
        assert False

