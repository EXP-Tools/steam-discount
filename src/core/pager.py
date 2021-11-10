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
from src.cfg import enum
from src.utils import num
from src.utils import log

HTML_DISCOUNT_PATH = '%s/docs/discount.html' % env.PRJ_DIR
HTML_ZERO_PATH = '%s/docs/zero.html' % env.PRJ_DIR
HTML_EVALUATION_PATH = '%s/docs/evaluation.html' % env.PRJ_DIR
HTML_HOT_PATH = '%s/docs/hot.html' % env.PRJ_DIR

TPL_DISCOUNT_PATH = '%s/tpl/html_discount.tpl' % env.PRJ_DIR
TPL_ZERO_PATH = '%s/tpl/html_zero.tpl' % env.PRJ_DIR
TPL_EVALUATION_PATH = '%s/tpl/html_evaluation.tpl' % env.PRJ_DIR
TPL_HOT_PATH = '%s/tpl/html_hot.tpl' % env.PRJ_DIR
TPL_HEAD_PATH = '%s/tpl/head.tpl' % env.PRJ_DIR
TPL_TAIL_PATH = '%s/tpl/tail.tpl' % env.PRJ_DIR
TPL_TABLE_PATH = '%s/tpl/table.tpl' % env.PRJ_DIR
TPL_ROW_PATH = '%s/tpl/row.tpl' % env.PRJ_DIR


def to_page(limit=500) :
    sdbc = SqliteDBC(env.DB_PATH)
    sdbc.conn()
    _to_page(sdbc, TSteamGame.i_discount_rate, False, limit, TPL_DISCOUNT_PATH, HTML_DISCOUNT_PATH, 'and %s > 6' % TSteamGame.i_evaluation_id)
    _to_page(sdbc, TSteamGame.s_discount_price, False, limit, TPL_ZERO_PATH, HTML_ZERO_PATH, 'and %s in ("%s")' % (TSteamGame.s_discount_price, '", "'.join(enum.FREES)))
    _to_page(sdbc, TSteamGame.i_evaluation_id, False, limit, TPL_EVALUATION_PATH, HTML_EVALUATION_PATH)
    _to_page(sdbc, TSteamGame.i_rank_id, True, limit, TPL_HOT_PATH, HTML_HOT_PATH)
    sdbc.close()

    
def _to_page(sdbc, column, order, limit, tpl_path, savepath, condition='') :
    print(condition)
    tpl_index, tpl_head, tpl_tail, tpl_table, tpl_row = load_tpl(tpl_path)
    games = query_game(sdbc, column, order, limit, condition)
    rows = []
    for g in games:
        new_flag = compare(g.original_price, g.lowest_price, g.discount_price)
        row = tpl_row % {
            'img_url': num.byte_to_str(g.img_url) or '',
            'game_id': g.game_id or 0,
            'game_name': num.byte_to_str(g.game_name) or '',
            'original_price': num.byte_to_str(g.original_price) or '',
            'lowest_price': num.byte_to_str(g.lowest_price) or '',
            'discount_rate': g.discount_rate or 0,
            'discount_price': num.byte_to_str(g.discount_price) or '',
            'new_flag': new_flag, 
            'evaluation': num.byte_to_str(g.evaluation) or '',
            'evaluation_info': num.byte_to_str(g.evaluation_info) or '',
            'rank_id': g.rank_id or 0,
            'cur_player_num': g.cur_player_num or 0,
            'today_max_player_num': g.today_max_player_num or 0,
            'shop_url': num.byte_to_str(g.shop_url) or ''
        }
        rows.append(row)

    table = tpl_table % {
        'rows': '\n'.join(rows)
    }

    index = tpl_index % {
        'head': tpl_head, 
        'tail': tpl_tail, 
        'datetime': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) ,
        'limit': limit, 
        'table': table
    }

    create_html(index, savepath)
    log.info('生成页面 [%s] 成功' % savepath)


def load_tpl(tpl_path) :
    with open(tpl_path, 'r', encoding=env.CHARSET) as file:
        tpl_index = file.read()

    with open(TPL_HEAD_PATH, 'r', encoding=env.CHARSET) as file:
        tpl_head = file.read()

    with open(TPL_TAIL_PATH, 'r', encoding=env.CHARSET) as file:
        tpl_tail = file.read()

    with open(TPL_TABLE_PATH, 'r', encoding=env.CHARSET) as file:
        tpl_table = file.read()

    with open(TPL_ROW_PATH, 'r', encoding=env.CHARSET) as file:
        tpl_row = file.read()

    return tpl_index, tpl_head, tpl_tail, tpl_table, tpl_row


def query_game(conn, column, order, limit, condition='') :
    dao = TSteamGameDao()
    sort_by = 'asc' if order else 'desc'
    where = " %s and %s is not null order by %s %s limit %i" % (condition, column, column, sort_by, limit)
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


def compare(original, lowest, discount) :
    new_flag = ''
    if original and lowest and discount :
        org = num.to_float(original)
        low = num.to_float(lowest)
        dis = num.to_float(discount)
        low = low + 0.01  # 精度误差
        if dis <= low and low < org :
            new_flag = ' <img src="imgs/lowest.gif" />'
    return new_flag
