#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author : EXP
# -----------------------------------------------

import time
import random
import argparse
from pypdm.dbc._sqlite import SqliteDBC
from src.core.steam_crawler import SteamCrawler
from src.config import settings
from src.core import saver
from src.core import pager
from src.core import archive
from src.core import assets
from color_log.clog import log


GIT_CRAWL_PWD = "3uJtWFf4Vx1S2dSQXJCK"
UPDATED_GAME_IDS = set()

def args() :
    parser = argparse.ArgumentParser(
        prog='', # 会被 usage 覆盖
        usage='Steam 特惠游戏榜单 - 帮助信息',
        description='从商城爬取游戏的【打折】【零元购】【测评】【热度】情况的榜单整理并展示',
        epilog='\r\n'.join([
            '无代理: ',
            '  python main.py -p 4 -l 100',
            '有代理: ',
            '  python main.py -p 4 -l 100 -c "127.0.0.1:18888"',
        ])
    )
    parser.add_argument('-g', '--git', dest='git', type=str, default=GIT_CRAWL_PWD, help='Github Action 的启动密码（避免被 Fork 时别人可以直接运行，导致目标站点被 DDos）')
    parser.add_argument('-c', '--proxy', dest='proxy', type=str, default="", help='HTTP 代理服务，如 127.0.0.1:18888')
    parser.add_argument('-p', '--pages', dest='pages', type=int, default=4, help='爬取 steam 商城的游戏页数')
    parser.add_argument('-z', '--zone', dest='zone', type=str, default='CN', help='指定 steam 商城的地区，会影响售价单位')
    parser.add_argument('-s', '--specials', dest='specials', action='store_true', default=False, help='是否只爬取正在打折的游戏')
    parser.add_argument('-f', '--filter', dest='filter', type=str, default='globaltopsellers', help='其他过滤参数')
    parser.add_argument('-l', '--limit', dest='limit', type=int, default=100, help='每榜展示数量（最多 100）')
    return parser.parse_args()


def get_args(args) :
    if args.git != GIT_CRAWL_PWD :
        # Github Action 调用了 -g 参数，若仓库没有设置 secrets.CRAWL_PWD 会赋予为空值
        # 导致验证 Github Action 的 secrets.CRAWL_PWD 失败，爬虫进程终止执行
        # 目的是在仓库被 Fork 时，可以保护目标站点不被 DDos
        raise SystemExit('CRAWL_PWD 验证失败，请在仓库 Secrets 中配置正确的启动密码')

    proxy_svc = f'http://{args.proxy}'
    proxy = { "http": proxy_svc, "https": proxy_svc } if args.proxy else {}

    zone = args.zone or settings.steam['zone']
    specials = args.specials or settings.steam['specials']
    filter = args.filter or settings.steam['filter']
    pages = args.pages or settings.crawler['pages']
    limit = max(1, min(args.limit or settings.crawler['limit'], 100))
    return [ proxy, pages, zone, specials, filter, limit ]



def main(proxy, pages, zone, specials, filter, limit) :
    UPDATED_GAME_IDS.clear()
    assets.configure(zone, proxy)
    log.info('+++++++++++++++++++++++++++++++++++++++')
    rank_updated = update_rank(proxy)                          # 更新游戏排名
    if not update_top_discount(proxy, pages, zone, specials, filter):
        raise RuntimeError('所有热销页面均抓取失败，停止生成页面')
    update_random_discount(proxy, zone)         # 更新随机游戏的折扣信息（主要为了扩充数据库）
    pager.to_page(limit, include_hot=rank_updated, current_ids=UPDATED_GAME_IDS)
    archive.save(page_ids=pager.PUBLISHED_IDS)
    log.info('---------------------------------------')


def update_rank(proxy) :
    try :
        sc = SteamCrawler(settings.steam['game_stats_url'], proxy=proxy)

        log.info('正在抓取游戏排名数据 ...')
        html = sc.get_html()
        tsgs = sc.parse_rank(html)

        log.info('正在更新游戏排名数据 ...')
        saver.to_db(tsgs, True, False)
        return True
    except Exception as exc:
        log.error('更新游戏排名数据失败: %s' % exc)
        return False


def update_top_discount(proxy, pages, zone, specials, filter) :
    updated = 0
    for page in range(1, pages + 1) :
        updated += bool(_update_discount(proxy, page, zone, specials, filter))
        time.sleep(5)
    return updated


def update_random_discount(proxy, zone) :
    for cnt in range(2) :
        page = random.randint(1, settings.steam['total_pages'])
        _update_discount(proxy, page, zone, False, '')


def _update_discount(proxy, page, zone, specials, filter) :
    try :
        sc = SteamCrawler(settings.steam['game_price_url'], page, proxy, options={
            'cc': zone,
            'specials': 1 if specials else 0,
            'filter': filter
        })

        log.info('正在抓取第 [%i] 页的游戏数据 ...' % page)
        html = sc.get_html()
        tsgs = sc.parse_game(html)
        if not tsgs:
            log.warn('第 [%i] 页没有可更新的游戏' % page)
            return False

        log.info('正在更新第 [%i] 页的游戏数据 ...' % page)
        saver.to_db(tsgs, False, True)
        assets.record_availability(tsgs, zone)
        UPDATED_GAME_IDS.update(tsgs)
        return True
    except Exception as exc:
        log.error('更新第 [%i] 页的游戏数据失败: %s' % (page, exc))
        return False


def init() :
    import os
    fresh = not os.path.exists(settings.database['dbpath'])
    os.makedirs(os.path.dirname(settings.database['dbpath']) or '.', exist_ok=True)
    sdbc = SqliteDBC(options=settings.database)
    if not sdbc.exec_script(settings.database['sqlpath']):
        raise RuntimeError('初始化数据库失败')
    if fresh:
        archive.restore()



if __name__ == "__main__" :
    options = get_args(args())
    init()
    main(*options)
