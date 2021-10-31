#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -------------------------------
# PDM: t_steam_game
# -------------------------------

class TSteamGame :
    table_name = 't_steam_game'
    i_id = "i_id"
    s_name = "s_name"
    s_original_price = "s_original_price"
    s_lowest_price = "s_lowest_price"
    i_discount_rate = "i_discount_rate"
    s_discount_price = "s_discount_price"
    i_evaluation_id = "i_evaluation_id"
    s_evaluation = "s_evaluation"
    s_evaluation_info = "s_evaluation_info"
    s_shop_url = "s_shop_url"
    i_sort_id = "i_sort_id"
    i_cur_player_num = "i_cur_player_num"
    i_today_max_player_num = "i_today_max_player_num"


    def __init__(self) :
        self.id = None
        self.name = None
        self.original_price = None
        self.lowest_price = None
        self.discount_rate = None
        self.discount_price = None
        self.evaluation_id = None
        self.evaluation = None
        self.evaluation_info = None
        self.shop_url = None
        self.sort_id = None
        self.cur_player_num = None
        self.today_max_player_num = None


    def params(self) :
        return (
            self.name,
            self.original_price,
            self.lowest_price,
            self.discount_rate,
            self.discount_price,
            self.evaluation_id,
            self.evaluation,
            self.evaluation_info,
            self.shop_url,
            self.sort_id,
            self.cur_player_num,
            self.today_max_player_num,
        )


    def __repr__(self) :
        return '\n'.join(
            (
                '%s: {' % self.table_name,
                "    %s = %s" % (self.i_id, self.id),
                "    %s = %s" % (self.s_name, self.name),
                "    %s = %s" % (self.s_original_price, self.original_price),
                "    %s = %s" % (self.s_lowest_price, self.lowest_price),
                "    %s = %s" % (self.i_discount_rate, self.discount_rate),
                "    %s = %s" % (self.s_discount_price, self.discount_price),
                "    %s = %s" % (self.i_evaluation_id, self.evaluation_id),
                "    %s = %s" % (self.s_evaluation, self.evaluation),
                "    %s = %s" % (self.s_evaluation_info, self.evaluation_info),
                "    %s = %s" % (self.s_shop_url, self.shop_url),
                "    %s = %s" % (self.i_sort_id, self.sort_id),
                "    %s = %s" % (self.i_cur_player_num, self.cur_player_num),
                "    %s = %s" % (self.i_today_max_player_num, self.today_max_player_num),
                '}\n'
            )
        )
