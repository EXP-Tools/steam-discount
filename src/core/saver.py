#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author : EXP
# -----------------------------------------------

import re
from pypdm.dbc._sqlite import SqliteDBC
from src.dao.t_steam_game import TSteamGameDao
from src.cfg import env
from src.utils import log



def _to_float(s_price) :
    f_price = 0
    if s_price :
        try :
            f_price = re.search(r' (\d+(\.\d+)?)', s_price).group(1)
        except :
            log.error('解析价格异常')
    return float(f_price)



def to_db(new_tsgs, rank, discount) :
    '''
    创建或更新记录到数据库
    '''
    sdbc = SqliteDBC(env.DB_PATH)
    sdbc.conn()

    dao = TSteamGameDao()
    old_tsgs = dao.query_all(sdbc)

    # 重置排名
    if rank :
        for old_tsg in old_tsgs :
            old_tsg.rank_id = 0
            old_tsg.cur_player_num = 0
            old_tsg.today_max_player_num = 0
            dao.update(sdbc, old_tsg)

    # 更新游戏信息
    for old_tsg in old_tsgs :
        new_tsg = new_tsgs.get(old_tsg.game_id)
        if new_tsg is not None :
            compare(old_tsg, new_tsg, rank, discount)
            dao.update(sdbc, old_tsg)
            new_tsgs.pop(old_tsg.game_id)

    # 插入新游戏
    for id, tsg in new_tsgs.items() :
        dao.insert(sdbc, tsg)
 
    sdbc.close()


def compare(old, new, rank, discount) :
    old.game_name = old.game_name or new.game_name
    old.shop_url = old.shop_url or new.shop_url

    # 更新测评
    old.evaluation_id = new.evaluation_id or old.evaluation_id
    old.evaluation = new.evaluation or old.evaluation
    old.evaluation_info = new.evaluation_info or old.evaluation_info

    # 更新排名
    if rank :
        old.rank_id = new.rank_id
        old.cur_player_num = new.cur_player_num
        old.today_max_player_num = new.cur_player_num

    # 更新价格
    if discount :
        old.original_price = new.original_price or old.original_price
        old.discount_rate = new.discount_rate
        old.discount_price = new.discount_rate

        min = _to_float(old.lowest_price)
        cur = _to_float(new.lowest_price)
        if cur < min :
            old.lowest_price = new.lowest_price
            