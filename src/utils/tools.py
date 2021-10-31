#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author : EXP
# -----------------------------------------------

def byte_to_str(value) :
    if isinstance(value, bytes) :
        value = bytes.decode(value)
    return value
