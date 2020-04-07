# coding=utf-8

import FXIncome
from enum import Enum
import datetime as dt
import numpy as np

class CashFlow(object):
    """
    Member Attributes:
        cash_flow (list): 现金流量
        time_flow (list): 每笔现金流对应的未来时间，以年为单位
    """

    def __init__(self, cash_flow, time_flow):
        self.cash_flow = cash_flow
        self.time_flow = time_flow

    def npv(self, rate):
        npv = 0
        for cash, t in enumerate(self.cash_flow):
            npv += cash/((1+rate)**(self.time_flow[t]))

        return npv
