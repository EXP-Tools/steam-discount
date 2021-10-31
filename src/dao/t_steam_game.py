#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -------------------------------
# DAO: t_steam_game
# -------------------------------

from ..bean.t_steam_game import TSteamGame
from pypdm.dao._base import BaseDao


class TSteamGameDao(BaseDao) :
    TABLE_NAME = 't_steam_game'
    SQL_COUNT = 'select count(1) from t_steam_game'
    SQL_TRUNCATE = 'truncate table t_steam_game'
    SQL_INSERT = 'insert into t_steam_game(s_name, s_original_price, s_lowest_price, i_discount_rate, s_discount_price, i_evaluation_id, s_evaluation, s_evaluation_info, s_shop_url, i_rank_id, i_cur_player_num, i_today_max_player_num) values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
    SQL_DELETE = 'delete from t_steam_game where 1 = 1 '
    SQL_UPDATE = 'update t_steam_game set s_name = ?, s_original_price = ?, s_lowest_price = ?, i_discount_rate = ?, s_discount_price = ?, i_evaluation_id = ?, s_evaluation = ?, s_evaluation_info = ?, s_shop_url = ?, i_rank_id = ?, i_cur_player_num = ?, i_today_max_player_num = ? where 1 = 1 '
    SQL_SELECT = 'select i_id, s_name, s_original_price, s_lowest_price, i_discount_rate, s_discount_price, i_evaluation_id, s_evaluation, s_evaluation_info, s_shop_url, i_rank_id, i_cur_player_num, i_today_max_player_num from t_steam_game where 1 = 1 '

    def __init__(self) :
        BaseDao.__init__(self)

    def _to_bean(self, row) :
        bean = None
        if row:
            bean = TSteamGame()
            bean.id = self._to_val(row, 0)
            bean.name = self._to_val(row, 1)
            bean.original_price = self._to_val(row, 2)
            bean.lowest_price = self._to_val(row, 3)
            bean.discount_rate = self._to_val(row, 4)
            bean.discount_price = self._to_val(row, 5)
            bean.evaluation_id = self._to_val(row, 6)
            bean.evaluation = self._to_val(row, 7)
            bean.evaluation_info = self._to_val(row, 8)
            bean.shop_url = self._to_val(row, 9)
            bean.rank_id = self._to_val(row, 10)
            bean.cur_player_num = self._to_val(row, 11)
            bean.today_max_player_num = self._to_val(row, 12)
        return bean
