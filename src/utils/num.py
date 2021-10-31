#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author : EXP
# -----------------------------------------------

import re
from src.utils import log


def to_float(s_price) :
    f_price = 0
    if s_price :
        s_price = byte_to_str(s_price)
        try :
            f_price = float(re.search(r'(\d+(\.\d+)?)', s_price).group(1))
        except :
            log.error('解析价格异常: [%s]' % s_price)
    return f_price


def byte_to_str(value) :
    if isinstance(value, bytes) :
        value = bytes.decode(value)
    return value
