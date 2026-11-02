#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author : EXP
# @Time   : 2020/4/30 9:37
# @File   : page.py
# -----------------------------------------------
# 从数据库读取最新数据生成 GitHub 播报页面
# -----------------------------------------------

import html
from datetime import datetime, timedelta, timezone
from pypdm.dbc._sqlite import SqliteDBC
from src.bean.t_steam_game import TSteamGame
from src.dao.t_steam_game import TSteamGameDao
import src.config as config
import src.enum as enum
from src.utils import num
from color_log.clog import log
from src.core import assets

HTML_DISCOUNT_PATH = '%s/docs/discount.html' % config.PRJ_DIR
HTML_ZERO_PATH = '%s/docs/zero.html' % config.PRJ_DIR
HTML_EVALUATION_PATH = '%s/docs/evaluation.html' % config.PRJ_DIR
HTML_HOT_PATH = '%s/docs/hot.html' % config.PRJ_DIR

TPL_DISCOUNT_PATH = '%s/tpl/html_discount.tpl' % config.PRJ_DIR
TPL_ZERO_PATH = '%s/tpl/html_zero.tpl' % config.PRJ_DIR
TPL_EVALUATION_PATH = '%s/tpl/html_evaluation.tpl' % config.PRJ_DIR
TPL_HOT_PATH = '%s/tpl/html_hot.tpl' % config.PRJ_DIR
TPL_HEAD_PATH = '%s/tpl/head.tpl' % config.PRJ_DIR
TPL_TAIL_PATH = '%s/tpl/tail.tpl' % config.PRJ_DIR
TPL_TABLE_PATH = '%s/tpl/table.tpl' % config.PRJ_DIR
TPL_ROW_PATH = '%s/tpl/row.tpl' % config.PRJ_DIR
PUBLISHED_IDS = set()


def to_page(limit=100, include_hot=True, current_ids=None) :
    PUBLISHED_IDS.clear()
    current = (' and i_game_id in (%s)' % ','.join(str(int(i)) for i in current_ids)) if current_ids else ''
    limit = max(1, min(limit, 100))
    sdbc = SqliteDBC(options=config.settings.database)
    sdbc.conn()
    _to_page(sdbc, TSteamGame.i_discount_rate, False, limit, TPL_DISCOUNT_PATH, HTML_DISCOUNT_PATH,
        'and %s > %i and %s > 0 and %s < 100' % (
            TSteamGame.i_evaluation_id,
            enum.EVALUATIONS.get('Positive'),
            TSteamGame.i_discount_rate,
            TSteamGame.i_discount_rate
        ) + current
    )
    _to_page(sdbc, TSteamGame.i_evaluation_id, False, limit, TPL_ZERO_PATH, HTML_ZERO_PATH,
        ("and %s >= 100 and cast(s_original_price as text) != '0'" % TSteamGame.i_discount_rate) + current
    )
    _to_page(sdbc, TSteamGame.i_evaluation_id, False, limit, TPL_EVALUATION_PATH, HTML_EVALUATION_PATH)
    if include_hot:
        _to_page(sdbc, TSteamGame.i_rank_id, True, min(limit, 100), TPL_HOT_PATH, HTML_HOT_PATH)
    sdbc.close()
    assets.save(clean=include_hot)


def _to_page(sdbc, column, order, limit, tpl_path, savepath, condition='') :
    tpl_index, tpl_head, tpl_tail, tpl_table, tpl_row = load_tpl(tpl_path)
    games = query_game(sdbc, column, order, limit, condition)
    PUBLISHED_IDS.update(g.game_id for g in games)
    assets.prepare(games)
    rows = []
    for position, g in enumerate(games, 1):
        new_flag = compare(g.original_price, g.lowest_price, g.discount_price)
        row = tpl_row % {
            'position': '%02i' % position,
            'img_url': assets.cover_url(g),
            'game_id': g.game_id or 0,
            'game_name': html.escape(num.byte_to_str(g.game_name) or ''),
            'search': html.escape('%s %s' % (num.byte_to_str(g.game_name) or '', g.game_id), quote=True),
            'original_price': html.escape(num.byte_to_str(g.original_price) or '') if g.discount_rate else '',
            'lowest_price': html.escape(num.byte_to_str(g.lowest_price) or '—'),
            'discount_rate': g.discount_rate or 0,
            'discount_price': html.escape(num.byte_to_str(g.discount_price) or '—'),
            'discount_label': '-%i%%' % g.discount_rate if g.discount_rate else '—',
            'new_flag': new_flag,
            'evaluation': html.escape(num.byte_to_str(g.evaluation) or '暂无评价'),
            'evaluation_id': g.evaluation_id or 0,
            'evaluation_info': html.escape(num.byte_to_str(g.evaluation_info) or ''),
            'review_summary': html.escape((num.byte_to_str(g.evaluation_info) or '').split('。')[0]),
            'region_label': html.escape(assets.region_label(g)[0]),
            'region_notice': html.escape(assets.region_label(g)[1]),
            'rank_id': g.rank_id or 0,
            'cur_player_num': format(g.cur_player_num, ',') if g.cur_player_num is not None else '—',
            'today_max_player_num': format(g.today_max_player_num, ',') if g.today_max_player_num is not None else '—',
            'shop_url': html.escape(num.byte_to_str(g.shop_url) or '', quote=True)
        }
        rows.append(row)

    table = tpl_table % {
        'rows': '\n'.join(rows)
    }

    index = tpl_index % {
        'head': tpl_head,
        'tail': tpl_tail,
        'datetime': datetime.now(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M'),
        'count': len(games),
        'max_discount': '%i%%' % max((g.discount_rate or 0 for g in games), default=0),
        'featured': '\n'.join(
            '<a class="featured-game" href="%s" target="_blank" rel="noopener noreferrer">'
            '<img src="%s" width="104" height="40" alt=""><span><strong>%s</strong><small>%s</small>'
            '</span><span class="discount-badge" data-rate="%i">%s</span></a>' % (
                html.escape(num.byte_to_str(g.shop_url) or '', quote=True), assets.cover_url(g),
                html.escape(num.byte_to_str(g.game_name) or ''),
                html.escape(num.byte_to_str(g.discount_price) or '查看商店'), g.discount_rate or 0,
                '-%i%%' % g.discount_rate if g.discount_rate else 'PLAY') for g in games[:3]),
        'limit': limit,
        'table': table
    }

    create_html(index, savepath)
    log.info('生成页面 [%s] 成功' % savepath)


def load_tpl(tpl_path) :
    with open(tpl_path, 'r', encoding=config.CHARSET) as file:
        tpl_index = file.read()

    with open(TPL_HEAD_PATH, 'r', encoding=config.CHARSET) as file:
        tpl_head = file.read()

    with open(TPL_TAIL_PATH, 'r', encoding=config.CHARSET) as file:
        tpl_tail = file.read()

    with open(TPL_TABLE_PATH, 'r', encoding=config.CHARSET) as file:
        tpl_table = file.read()

    with open(TPL_ROW_PATH, 'r', encoding=config.CHARSET) as file:
        tpl_row = file.read()

    return tpl_index, tpl_head, tpl_tail, tpl_table, tpl_row


def query_game(conn, column, order, limit, condition='') :
    dao = TSteamGameDao()
    sort_by = 'asc' if order else 'desc'
    where = " %s and %s is not null order by %s %s, i_game_id limit %i" % (condition, column, column, sort_by, min(limit, 100))
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
    with open(savepath, 'w+', encoding=config.CHARSET) as file:
        file.write(data)


def compare(original, lowest, discount) :
    new_flag = ''
    if original and lowest and discount :
        org = num.to_float(original)
        low = num.to_float(lowest)
        dis = num.to_float(discount)
        low = low + 0.01  # 精度误差
        if dis <= low and low < org :
            new_flag = '<span class="low-badge">↘ 已记录史低</span>'
    return new_flag
