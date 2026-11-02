#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
from urllib.parse import urlencode, urlsplit, urlunsplit, parse_qsl

import requests
from bs4 import BeautifulSoup
from color_log.clog import log

import src.enum as enum
from src.bean.t_steam_game import TSteamGame


class SteamCrawler:
    def __init__(self, url, page=None, proxy=None, options=None):
        self.page = page or 1
        self.proxy = proxy or {}
        parts = urlsplit(url)
        self.options = dict(parse_qsl(parts.query))
        self.options.update(options or {})
        self.options.setdefault('l', 'schinese')
        self.options['page'] = self.page
        self.url = urlunsplit((parts.scheme, parts.netloc, parts.path,
                              urlencode({k: v for k, v in self.options.items()
                                         if v is not None and v != ''}), parts.fragment))

    def headers(self):
        return {
            'Accept': 'text/html,application/xhtml+xml',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        }

    def get_html(self):
        response = requests.get(self.url, headers=self.headers(),
                                proxies=self.proxy, timeout=(10, 30))
        response.raise_for_status()
        # Steam serves UTF-8; requests otherwise defaults text/html to ISO-8859-1.
        response.encoding = 'utf-8'
        if not response.text.strip():
            raise ValueError('Steam 返回了空页面: %s' % self.url)
        return response.text

    def parse_game(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        items = soup.select('a.search_result_row')
        if not items:
            if soup.select_one('#search_resultsRows') is not None:
                return {}
            raise ValueError('未找到 Steam 搜索结果，页面结构可能已变化')
        games = {}
        errors = 0
        for item in items:
            try:
                game = TSteamGame()
                game.game_name = item.select_one('.title').get_text(' ', strip=True)
                image = item.find('img')
                game.img_url = (image.get('src') or image.get('data-src')) if image else ''
                game.shop_url = item['href']
                self._prase_id(game, item)
                self._parse_price(game, item)
                self._parse_evaluation(game, item)
                if not game.is_garbled():
                    games[game.game_id] = game
            except (AttributeError, KeyError, TypeError, ValueError) as exc:
                errors += 1
                log.warn('跳过无法解析的商品 [%s]: %s' % (item.get('href', ''), exc))
        if not games:
            raise ValueError('Steam 搜索结果有 %i 条，但没有可用的价格记录' % len(items))
        if errors:
            log.warn('本页 %i 条商品中有 %i 条未能解析' % (len(items), errors))
        return games

    def _prase_id(self, game, item):
        # Bundles can also carry a comma-separated list of app IDs.
        match = re.search(r'/(?:app|sub|bundle)/(\d+)', game.shop_url)
        value = match.group(1) if match else (
            item.get('data-ds-packageid') or item.get('data-ds-appid') or
            item.get('data-ds-bundleid'))
        game.game_id = int(value)

    def _parse_price(self, game, item):
        final = item.select_one('.discount_final_price')
        original = item.select_one('.discount_original_price')
        rate = item.select_one('.discount_pct, .search_discount span')
        block = item.select_one('[data-discount]')
        game.discount_rate = int(block['data-discount']) if block else (
            int(re.sub(r'[^0-9]', '', rate.get_text()) or '0') if rate else 0)
        if final is not None:
            game.discount_price = self._free(final.get_text(' ', strip=True))
            game.original_price = (self._free(original.get_text(' ', strip=True))
                                   if original else game.discount_price)
        else:
            # Compatibility with the original Steam search markup.
            price = item.select_one('.search_price')
            if price is None:
                raise ValueError('没有公开售价（可能未发售或本地区不可购买）')
            strike = price.find(['strike', 's', 'del'])
            if strike:
                game.original_price = self._free(strike.get_text(' ', strip=True))
                strike.extract()
                game.discount_price = self._free(price.get_text(' ', strip=True))
            else:
                game.discount_price = self._free(price.get_text(' ', strip=True))
                game.original_price = game.discount_price
        if game.discount_price == '' or game.original_price == '':
            raise ValueError('价格为空')
        # Free-to-play is not a 100% discount; paid games given away are.
        if str(game.discount_price) == '0' and str(game.original_price) != '0':
            game.discount_rate = 100
        game.lowest_price = game.discount_price

    def _free(self, price):
        text = price.strip()
        if text.lower() in enum.FREES or re.fullmatch(r'[¥￥$€£]?\s*0(?:[.,]0+)?', text):
            return '0'
        return text

    def _parse_evaluation(self, game, item):
        summary = item.select_one('.search_review_summary')
        game.evaluation = '暂无评价'
        game.evaluation_info = ''
        if summary and summary.get('data-tooltip-html'):
            tooltip = BeautifulSoup(summary['data-tooltip-html'], 'html.parser')
            lines = list(tooltip.stripped_strings)
            if lines:
                game.evaluation = lines[0]
                game.evaluation_info = ' '.join(lines[1:]).replace(',', '')
        game.evaluation_id = enum.EVALUATIONS.get(game.evaluation)

    def parse_rank(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        games = {}
        # Current charts have changing CSS hashes. Use app links and numeric columns.
        rows = soup.select('table tr') or soup.select('.player_count_row')
        for row in rows:
            link = row.select_one('a[href*="/app/"]')
            if link is None:
                continue
            try:
                cells = row.find_all('td', recursive=False)
                counts = row.select('.currentServers')
                if not counts and len(cells) >= 5:
                    counts = cells[-2:]
                if len(counts) != 2:
                    raise ValueError('缺少当前在线和今日峰值列')
                game = TSteamGame()
                game.shop_url = link['href']
                game.game_id = int(re.search(r'/app/(\d+)', game.shop_url).group(1))
                links = row.select('a[href*="/app/"]')
                game.game_name = next(a.get_text(' ', strip=True) for a in links
                                      if a.get_text(' ', strip=True))
                image = row.find('img')
                game.img_url = image.get('src', '') if image else ''
                game.rank_id = (int(cells[1].get_text(strip=True)) if len(cells) >= 6
                                else len(games) + 1)
                game.cur_player_num, game.today_max_player_num = (
                    int(re.sub(r'[,\s\u00a0\u202f]', '', cell.get_text())) for cell in counts)
                games[game.game_id] = game
            except (AttributeError, KeyError, TypeError, ValueError, StopIteration) as exc:
                log.warn('跳过无法解析的热度记录: %s' % exc)
        if not games:
            raise ValueError('未找到 Steam 热度榜数据，保留已有排名')
        return games
