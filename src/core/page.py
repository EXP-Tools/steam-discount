#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author : EXP
# @Time   : 2020/4/30 9:37
# @File   : page.py
# -----------------------------------------------
# 从数据库读取最新数据生成 GitHub 播报页面
# -----------------------------------------------

import time
from pypdm.dbc._sqlite import SqliteDBC
from src.bean.t_steam_game import TSteamGame
from src.dao.t_steam_game import TSteamGameDao
from src.cfg import env
from src.utils import log

HTML_DISCOUNT_PATH = '%s/docs/index_discount.html' % env.PRJ_DIR
HTML_EVALUATION_PATH = '%s/docs/index_evaluation.html' % env.PRJ_DIR
HTML_HOT_PATH = '%s/docs/index_hot.html' % env.PRJ_DIR

TPL_DISCOUNT_PATH = '%s/tpl/index_discount.tpl' % env.PRJ_DIR
TPL_EVALUATION_PATH = '%s/tpl/index_evaluation.tpl' % env.PRJ_DIR
TPL_HOT_PATH = '%s/tpl/index_hot.tpl' % env.PRJ_DIR
TPL_TABLE_PATH = '%s/tpl/table.tpl' % env.PRJ_DIR
TPL_ROW_PATH = '%s/tpl/row.tpl' % env.PRJ_DIR


def to_page(limit = 100) :
    sdbc = SqliteDBC(env.DB_PATH)
    sdbc.conn()
    _to_page(sdbc, TSteamGame.i_discount_rate, 'desc', limit, TPL_DISCOUNT_PATH, HTML_DISCOUNT_PATH)
    _to_page(sdbc, TSteamGame.i_evaluation_id, 'desc', limit, TPL_EVALUATION_PATH, HTML_EVALUATION_PATH)
    _to_page(sdbc, TSteamGame.i_rank_id, 'asc', limit, TPL_HOT_PATH, HTML_HOT_PATH)
    sdbc.close()

    
def _to_page(sdbc, column, order, limit, tpl_path, savepath) :
    tpl_index, tpl_table, tpl_row = load_tpl(tpl_path)
    games = query_game(sdbc, column, order, limit)
    rows = []
    for g in games:
        new_flag = ''
        if g.original_price and g.lowest_price and g.discount_price :
            if g.lowest_price < g.original_price and g.discount_price <= g.lowest_price :
                new_flag = ' <img src="imgs/lowest.gif" />'

        row = tpl_row % {
            'img_url': byte_to_str(g.img_url) or '',
            'game_id': g.game_id or 0,
            'game_name': byte_to_str(g.game_name) or '',
            'original_price': byte_to_str(g.original_price) or '',
            'lowest_price': byte_to_str(g.lowest_price) or '',
            'discount_rate': g.discount_rate or 0,
            'discount_price': byte_to_str(g.discount_price) or '',
            'new_flag': new_flag, 
            'evaluation': byte_to_str(g.evaluation) or '',
            'rank_id': g.rank_id or 0,
            'cur_player_num': g.cur_player_num or 0,
            'today_max_player_num': g.today_max_player_num or 0,
            'shop_url': byte_to_str(g.shop_url) or ''
        }
        rows.append(row)

    table = tpl_table % {
        'rows': '\n'.join(rows)
    }

    index = tpl_index % {
        'datetime': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) ,
        'table': table
    }

    create_html(index, savepath)
    log.info('生成页面 [%s] 成功' % savepath)


def load_tpl(tpl_path) :
    with open(tpl_path, 'r', encoding=env.CHARSET) as file:
        tpl_index = file.read()

    with open(TPL_TABLE_PATH, 'r', encoding=env.CHARSET) as file:
        tpl_table = file.read()

    with open(TPL_ROW_PATH, 'r', encoding=env.CHARSET) as file:
        tpl_row = file.read()

    return tpl_index, tpl_table, tpl_row


def query_game(conn, column, order, limit) :
    dao = TSteamGameDao()
    where = " and %s is not null order by %s %s limit %d" % (column, column, order, limit)
    sql = TSteamGameDao.SQL_SELECT + where
    beans = []
    try:
        cursor = conn.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        for row in rows:
            bean = dao._to_bean(row)
            beans.append(bean)
        cursor.close()
    except:
        log.error("从表 [%s] 查询数据失败" % TSteamGame.table_name)
    return beans


def create_html(data, savepath) :
    with open(savepath, 'w+', encoding=env.CHARSET) as file:
        file.write(data)


def byte_to_str(value) :
    if isinstance(value, bytes) :
        value = bytes.decode(value)
    return value
