#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author : EXP
# -----------------------------------------------

import sys
import time
from pypdm.dbc._sqlite import SqliteDBC
from src.core.steam_crawler import SteamCrawler
from src.cfg import env
from src.core import saver
from src.utils import log



def main(is_help, pages, zone, specials, filter) :
    if is_help :
        log.info(help_info())

    log.info('+++++++++++++++++++++++++++++++++++++++')
    # update_discount(pages, zone, specials, filter)  # 更新游戏折扣信息
    update_rank()                                   # 更新游戏排名
    log.info('---------------------------------------')


def help_info() :
    return '''
    
'''


def update_discount(pages, zone, specials, filter) :
    for page in range(1, pages + 1) :
        time.sleep(1)
        try :
            sc = SteamCrawler(env.STEAM_GAME_PRICE_URL, page, options={
                'cc': zone,
                'specials': 1 if specials else 0,
                'filter': filter
            })

            log.info('正在抓取第 [%i/%i] 页的游戏折扣数据 ...' % (page, pages))
            html = sc.get_html()
            tsgs = sc.parse_game(html)

            log.info('正在更新第 [%i/%i] 页的游戏折扣数据 ...' % (page, pages))
            saver.to_db(tsgs, False, True)
            
        except :
            log.error('更新第 [%i/%i] 页的游戏折扣数据失败' % (page, pages))



def update_rank() :
    try :
        sc = SteamCrawler(env.STEAM_GAME_STATS_URL)

        log.error('正在抓取游戏排名数据 ...')
        html = sc.get_html()
        tsgs = sc.parse_rank(html)

        log.error('正在更新游戏排名数据 ...')
        saver.to_db(tsgs, True, False)
    except :
        log.error('更新游戏排名数据失败')


def init() :
    log.init()
    sdbc = SqliteDBC(env.DB_PATH)
    sdbc.exec_script(env.SQL_PATH)


def sys_args(sys_args) :
    is_help = False
    pages = 10          # 最大爬取页数
    zone = 'CN'         # 价格区域
    specials = False    # 仅特惠游戏
    filter = 'globaltopsellers'    # 全球热销游戏
    
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
                zone = int(sys_args[idx])

            elif sys_args[idx] == '-s' or sys_args[idx] == '--specials' :
                idx += 1
                specials = sys_args[idx]

            elif sys_args[idx] == '-f' or sys_args[idx] == '--filter' :
                idx += 1
                filter = sys_args[idx]

        except :
            pass
        idx += 1
    return is_help, pages, zone, specials, filter


if __name__ == "__main__" :
    init()
    try :
        main(*sys_args(sys.argv))
    except :
        log.error('未知异常')
