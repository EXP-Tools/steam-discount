#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author : EXP
# -----------------------------------------------

import requests
from urllib.parse import quote
from bs4 import BeautifulSoup
from src.cfg import env
from src.cfg.evaluation import EVALUATION
from src.bean.t_steam_game import TSteamGame
from src.utils import log



class SteamCrawler :

    def __init__(self, url, page, options={}) :
        kvs = self._concat_kvs(page, options)
        self.url = '%s?%s' % (url, kvs)


    def _concat_kvs(self, page, options) :
        self.options = options or {}
        self._add_kv('page', page or 1)
        kvs = []
        for key, val in self.options.items() :
            kv = '%s=%s' % (key, quote(str(val), env.CHARSET))
            kvs.append(kv)
        return '&'.join(kvs)


    def _add_kv(self, key, value) :
        if key and value :
            self.options[key] = value


    def headers(self):
        return {
            'Accept' : '*/*',
            'Accept-Encoding' : 'gzip, deflate',
            'Accept-Language' : 'zh-CN,zh;q=0.9',
            'Connection' : 'keep-alive',
            'User-Agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36',
        }

    
    def get_html(self) :
        html = ''
        try :
            response = requests.get(self.url, headers=self.headers())
            if response.status_code == 200 :
                response.encoding = response.apparent_encoding
                html = response.text
            else :
                log.error('爬取 steam 游戏优惠信息失败：HTTP %i' % response.status)
        except:
            log.error('爬取 steam 游戏优惠信息失败')
        return html


    def parse(self, html) :
        tsgs = {}
        soup = BeautifulSoup(html, "html.parser")
        items = soup.find_all(class_="search_result_row ds_collapse_flag")
        for item in items :
            tsg = TSteamGame()
            self._prase_id(tsg, item)
            tsg.name = item.find('span', class_='title').text
            self._parse_price(tsg, item)
            self._parse_evaluation(tsg, item)
            tsg.shop_url = item.get('href')
            tsgs[tsg.id] = (tsg)
        return tsgs


    def _prase_id(self, tsg, item) :
        '''
        解析游戏 ID :
            package: DLC
            app: 游戏本体
            bundle: 捆绑包
        '''
        # 赋值顺序不能变
        id = item.get('data-ds-packageid') or \
             item.get('data-ds-appid') or \
             item.get('data-ds-bundleid')
        tsg.id = int(id)


    def _parse_price(self, tsg, item) :
        '''
        解析游戏价格
        '''
        # 折扣率
        div = item.find('div', class_='col search_discount responsive_secondrow')

        # 没有折扣
        if not div.text.strip() :
            div = item.find('div', class_='col search_price responsive_secondrow')
            tsg.original_price = div.text.strip()

        # 有折扣
        else :
            tsg.discount_rate = int(div.span.text.replace('-', '').replace('%', '').strip())
            div = item.find('div', class_='col search_price discounted responsive_secondrow')
            tsg.original_price = div.strike.text.strip()
            tsg.discount_price = div.text.strip().split('\n')[-1].strip()
            

    def _parse_evaluation(self, tsg, item) :
        '''
        解析游戏评价
        '''
        span = item.find('span', class_='search_review_summary positive')
        if not span :
            tsg.evaluation_info = ''
            tsg.evaluation = '暂无评价'
        else :
            info = span.get('data-tooltip-html').strip().split('<br>')
            tsg.evaluation_info = info[1]
            tsg.evaluation = info[0]
        tsg.evaluation_id = EVALUATION.get(tsg.evaluation, -1)


