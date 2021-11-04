#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author : EXP
# -----------------------------------------------

import sys
import time
import random
from pypdm.dbc._sqlite import SqliteDBC
from src.core.steam_crawler import SteamCrawler
from src.cfg import env
from src.core import saver
from src.core import page
from src.utils import log


def help_info() :
    return '''
-h           查看帮助信息
-p <pages>   爬取 steam 商城的游戏页数，默认 5
-z <zone>    指定 steam 商城的地区，会影响售价单位，默认 CN （RMB）
-s           是否只爬取正在打折的游戏，默认不指定
-f <filter>  其他过滤参数，默认 globaltopsellers
-l <limit>   最终界面展示的游戏数量，默认 500
'''


def main(is_help, pages, zone, specials, filter, limit) :
    if is_help :
        log.info(help_info())
        return

    log.info('+++++++++++++++++++++++++++++++++++++++')
    update_rank()                                       # 更新游戏排名
    update_top_discount(pages, zone, specials, filter)  # 更新销售 top 的游戏的折扣信息
    update_random_discount(zone)         # 更新随机游戏的折扣信息（主要为了扩充数据库）
    page.to_page(limit)
    log.info('---------------------------------------')



def update_rank() :
    try :
        sc = SteamCrawler(env.STEAM_GAME_STATS_URL)

        log.info('正在抓取游戏排名数据 ...')
        html = sc.get_html()
        tsgs = sc.parse_rank(html)

        log.info('正在更新游戏排名数据 ...')
        saver.to_db(tsgs, True, False)
    except :
        log.error('更新游戏排名数据失败')


def update_top_discount(pages, zone, specials, filter) :
    for page in range(1, pages + 1) :
        _update_discount(page, zone, specials, filter)
        time.sleep(5)


def update_random_discount(zone) :
    for cnt in range(1, 10) :
        page = random.randint(1, 1000)
        _update_discount(page, zone, False, '')


def _update_discount(page, zone, specials, filter) :
    try :
        sc = SteamCrawler(env.STEAM_GAME_PRICE_URL, page, options={
            'cc': zone,
            'specials': 1 if specials else 0,
            'filter': filter
        })

        log.info('正在抓取第 [%i] 页的游戏数据 ...' % page)
        html = sc.get_html()
        tsgs = sc.parse_game(html)

        log.info('正在更新第 [%i] 页的游戏数据 ...' % page)
        saver.to_db(tsgs, False, True)
    except :
        log.error('更新第 [%i] 页的游戏数据失败' % page)


def init() :
    log.init()
    sdbc = SqliteDBC(env.DB_PATH)
    sdbc.exec_script(env.SQL_PATH)


def sys_args(sys_args) :
    is_help = False
    pages = 5           # 最大爬取页数
    zone = 'CN'         # 价格区域
    specials = False    # 仅特惠游戏
    filter = 'globaltopsellers'    # 全球热销游戏
    limit = 500         # 页面限制展示数

    idx = 1
    size = len(sys_args)
    while idx < size :
        try :
            if sys_args[idx] == '-h' or sys_args[idx] == '--help' :
                is_help = True
                break

            elif sys_args[idx] == '-p' or sys_args[idx] == '--pages' :
                idx += 1
                pages = int(sys_args[idx])

            elif sys_args[idx] == '-z' or sys_args[idx] == '--zone' :
                idx += 1
                zone = sys_args[idx]

            elif sys_args[idx] == '-s' or sys_args[idx] == '--specials' :
                specials = True

            elif sys_args[idx] == '-f' or sys_args[idx] == '--filter' :
                idx += 1
                filter = sys_args[idx]

            elif sys_args[idx] == '-l' or sys_args[idx] == '--limit' :
                idx += 1
                limit = int(sys_args[idx])
        except :
            pass
        idx += 1
    return is_help, pages, zone, specials, filter, limit


if __name__ == "__main__" :
    init()
    try :
        main(*sys_args(sys.argv))
    except :
        log.error('未知异常')
