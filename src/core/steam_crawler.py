#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author : EXP
# -----------------------------------------------

import re
import requests
from urllib.parse import quote
from bs4 import BeautifulSoup
from src.cfg import env
from src.cfg import enum
from src.bean.t_steam_game import TSteamGame
from src.utils import log



class SteamCrawler :

    def __init__(self, url, page=None, options={}) :
        self.url = url
        self.page = page
        kvs = self._concat_kvs(page, options)
        if len(kvs) > 0 :
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


    def parse_game(self, html) :
        tsgs = {}
        soup = BeautifulSoup(html, "html.parser")
        items = soup.find_all(class_="search_result_row ds_collapse_flag")
        for item in items :
            tsg = TSteamGame()
            tsg.game_name = item.find('span', class_='title').text
            tsg.garbled = self.contain_garbled(tsg.game_name)
            tsg.img_url = item.find('img').get('src')
            tsg.shop_url = item.get('href')
            self._parse_evaluation(tsg, item)
            self._prase_id(tsg, item)
            self._parse_price(tsg, item)
            
            if not tsg.garbled :    # 偶发的乱码问题，下次再爬取即可
                tsgs[tsg.game_id] = tsg
        return tsgs

    
    def _prase_id(self, tsg, item) :
        '''
        解析游戏 ID :
            package: DLC
            app: 游戏本体
            bundle: 捆绑包
        '''
        # 赋值顺序不能变
        game_id = item.get('data-ds-packageid') or \
                  item.get('data-ds-appid') or \
                  item.get('data-ds-bundleid') or \
                  re.search(r'/(\d+)', tsg.shop_url).group(1)
        tsg.game_id = int(game_id)


    def _parse_price(self, tsg, item) :
        '''
        解析游戏价格
        '''
        # 折扣率
        div = item.find('div', class_='col search_discount responsive_secondrow')

        # 没有折扣
        if not div.text.strip() :
            tsg.discount_rate = 0
            div = item.find('div', class_='col search_price responsive_secondrow')
            tsg.garbled = self.contain_garbled(div.text)
            tsg.original_price = self._free(div.text.strip())
            tsg.discount_price = tsg.original_price
            tsg.lowest_price = tsg.original_price

        # 有折扣
        else :
            tsg.discount_rate = int(div.span.text.replace('-', '').replace('%', '').strip())
            div = item.find('div', class_='col search_price discounted responsive_secondrow')
            tsg.garbled = self.contain_garbled(div.text)
            tsg.original_price = self._free(div.strike.text.strip())
            tsg.discount_price = self._free(re.search(r'<br/>(.+)</div>', div.__repr__(), re.I).group(1).strip())
            tsg.lowest_price = tsg.discount_price

        if str(tsg.discount_price) == '0' :
            tsg.discount_rate = 100
        


    def _free(self, price) :
        if price.lower().strip() in enum.FREES :
            price = 0
        return price
    

    def _parse_evaluation(self, tsg, item) :
        '''
        解析游戏测评
        '''
        span = item.find('span', class_='search_review_summary positive')
        if not span :
            tsg.evaluation_info = ''
            tsg.evaluation = '暂无评价'
        else :
            _evaluation = span.get('data-tooltip-html').strip()
            tsg.garbled = self.contain_garbled(_evaluation)
            info = _evaluation.split('<br>')
            tsg.evaluation_info = info[1].replace(',', '')
            tsg.evaluation = info[0]
        tsg.evaluation_id = enum.EVALUATIONS.get(tsg.evaluation)


    def parse_rank(self, html) :
        tsgs = {}
        rank = 0

        soup = BeautifulSoup(html, "html.parser")
        items = soup.find_all(class_="player_count_row")
        for item in items :
            rank += 1
            tsg = TSteamGame()
            tsg.rank_id = rank

            a = item.find('a', class_='gameLink')
            tsg.shop_url = a.get('href')
            tsg.game_id = int(re.search(r'/(\d+)', tsg.shop_url).group(1))
            tsg.game_name = re.sub(r'\s+', ' ', a.text, re.M).strip()

            spans = item.find_all('span', class_='currentServers')
            tsg.cur_player_num = int(spans[0].text.strip().replace(',', ''))
            tsg.today_max_player_num = int(spans[1].text.strip().replace(',', ''))

            tsgs[tsg.game_id] = (tsg)
        return tsgs

    
    def contain_garbled(self, text) :
        is_garbled = False
        if 'Â' in text or 'å' in text :
            is_garbled = True
        return is_garbled



