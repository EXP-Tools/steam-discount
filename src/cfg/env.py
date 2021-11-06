#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author : EXP
# -----------------------------------------------

import os
PRJ_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)
CHARSET = 'utf-8'

SQL_PATH = '%s/script/cves-create.sql' % PRJ_DIR
DB_PATH =  '%s/data/steam.db' % PRJ_DIR

STEAM_GAME_PRICE_URL = 'https://store.steampowered.com/search/'
STEAM_GAME_STATS_URL = 'https://store.steampowered.com/stats/'
STEAM_TOTAL_PAGES = 5000
