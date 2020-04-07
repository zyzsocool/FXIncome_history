# coding=utf-8

import FXIncome
from enum import Enum
import datetime as dt
import numpy as np

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


class Bond(FXIncome):
    """
    Class Types:
    根据付息方式的不同，分三类债券讨论：贴现债券、附息债券、到期一次还本付息的债券
    Member Attributes:
        sid (string): 债券代码
        name (string): 债券名称
        coupon_date (datetime): 债券的起息日
        coupon_rate (float): 债券的票面利率
        coupon_type (Enum): '贴现'、'附息'、'到期一次还本付息'
        end_date (datetime): 债券的到期日
        coupon_frequency (int): 每年支付利率次数
    """

    def __init__(self, sid, name, coupon_date, coupon_rate, coupon_type, end_date, coupon_frequency):
        self.sid = sid
        self.name = name
        self.coupon_date = coupon_date
        self.coupon_rate = coupon_rate
        self.coupon_type = coupon_type
        self.end_date = end_date
        self.coupon_frequency = coupon_frequency

    def __str__(self):
        items = list()
        items.append('--- Bond Begin')
        items.append('- 代码: {}'.format(self.sid))
        items.append('- 名称: {}'.format(self.name))
        items.append('- 起息日: {}'.format(self.coupon_date))
        items.append('- 票面利率: {}'.format(self.coupon_rate))
        items.append('- 付息类型: {}'.format(self.coupon_type.value))
        items.append('- 到期日: {}'.format(self.end_date))
        items.append('--- Bond End')
        return '\n'.join(items)

    def cal_pv(self, assessment_date, discount_rate):
        """
        根据评估日和折现率，计算出评估日的现值。

        Args:
            size (int): amount to update the position size
                size < 0: A sell operation has taken place
                size > 0: A buy operation has taken place

            price (float):
                Must always be positive to ensure consistency

        Returns:
            A tuple (non-named) contaning
               size - new position size
                   Simply the sum of the existing size plus the "size" argument
               price - new position price
                   If a position is increased the new average price will be
                   returned
                   If a position is reduced the price of the remaining size
                   does not change
                   If a position is closed the price is nullified
                   If a position is reversed the price is the price given as
                   argument
               opened - amount of contracts from argument "size" that were used
                   to open/increase a position.
                   A position can be opened from 0 or can be a reversal.
                   If a reversal is performed then opened is less than "size",
                   because part of "size" will have been used to close the
                   existing position
               closed - amount of units from arguments "size" that were used to
                   close/reduce a position

            Both opened and closed carry the same sign as the "size" argument
            because they refer to a part of the "size" argument
        """
        return self.pv
