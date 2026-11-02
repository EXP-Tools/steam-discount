#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author : EXP
# -----------------------------------------------

import sqlite3
from src.dao.t_steam_game import TSteamGameDao
import src.config as config
from src.utils import num



def to_db(new_tsgs, rank, discount) :
    '''
    创建或更新记录到数据库
    '''
    if not new_tsgs:
        return  # Never clear cached ranks after an empty/failed response.
    dao = TSteamGameDao()
    pending = dict(new_tsgs)
    conn = sqlite3.connect(config.settings.database['dbpath'])
    try:
        with conn:
            old_tsgs = [dao._to_bean(row) for row in conn.execute(dao.SQL_SELECT)]
            if rank:
                conn.execute('UPDATE t_steam_game SET i_rank_id = NULL, '
                             'i_cur_player_num = NULL, i_today_max_player_num = NULL')
            for old in old_tsgs:
                new = pending.pop(old.game_id, None)
                if new is not None:
                    compare(old, new, rank, discount)
                    conn.execute(dao.SQL_UPDATE + ' AND i_id = ?', old.params() + (old.id,))
            for game in pending.values():
                conn.execute(dao.SQL_INSERT, game.params())
    finally:
        conn.close()


def compare(old, new, rank, discount) :
    old.game_name = new.game_name or old.game_name
    old.shop_url = new.shop_url or old.shop_url
    old.img_url = new.img_url or old.img_url

    # 更新排名
    if rank :
        old.rank_id = new.rank_id
        old.cur_player_num = new.cur_player_num
        old.today_max_player_num = new.today_max_player_num

    # 更新测评
    if discount :
        old.evaluation_id = new.evaluation_id
        old.evaluation = new.evaluation
        old.evaluation_info = new.evaluation_info

    # 更新价格
    if discount :
        if new.original_price is not None:
            old.original_price = new.original_price
        old.lowest_price = old.lowest_price or new.lowest_price
        old.discount_rate = new.discount_rate
        old.discount_price = new.discount_price

        if str(old.discount_price) == '0' and str(old.original_price) != '0':
            old.discount_rate = 100

        min = num.to_float(old.lowest_price)
        cur = num.to_float(new.lowest_price)
        if cur < min :
            old.lowest_price = new.lowest_price



