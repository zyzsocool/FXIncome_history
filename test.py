from enum import Enum
import datetime


class CouponType(Enum):
    DISCOUNT = '贴现'
    COUPON = '附息'
    LAST = '到期一次还本付息'

    @staticmethod
    def from_str(label):
        if label in ('贴现'):
            return CouponType.DISCOUNT
        elif label in ('附息'):
            return CouponType.COUPON
        elif label in ('到期一次还本付息'):
            return CouponType.LAST
        else:
            raise NotImplementedError


text = '到期一次还本付息'
ct = CouponType.from_str(text)
print(ct.value)
if ct is CouponType.LAST:
    print('at last')
else:
    print('my god')


