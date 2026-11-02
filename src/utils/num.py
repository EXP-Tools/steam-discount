#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author : EXP
# -----------------------------------------------

import re
from color_log.clog import log
import src.enum as enum


def to_float(s_price) :
    f_price = 0
    s_price = byte_to_str(s_price)
    if s_price in enum.FREES :
        f_price = 0

    elif s_price :
        s_price = byte_to_str(s_price)
        try :
            value = re.search(r'\d[\d.,\s\u00a0\u202f]*', str(s_price)).group(0)
            value = re.sub(r'\s', '', value)
            if ',' in value and '.' in value:
                # The last separator is decimal (1,299.99 or 1.299,99).
                if value.rfind(',') > value.rfind('.'):
                    value = value.replace('.', '').replace(',', '.')
                else:
                    value = value.replace(',', '')
            elif ',' in value:
                parts = value.split(',')
                value = ''.join(parts) if len(parts[-1]) == 3 else ''.join(parts[:-1]) + '.' + parts[-1]
            f_price = float(value)
        except :
            log.error('解析价格异常: [%s]' % s_price)
    return f_price


def byte_to_str(value) :
    if isinstance(value, bytes) :
        value = bytes.decode(value)
    return value
