#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author : EXP
# -----------------------------------------------

import sqlite3
import requests
import pandas as pd
from bs4 import BeautifulSoup

from pypdm.builder import build
from src.cfg import env
from pypdm.dbc._sqlite import SqliteDBC
from src.utils import log


num = 0



class SteamCrawler :

    def __init__(self, url) :
        # https://store.steampowered.com/search/?cc=CN&filter=globaltopsellers&page=1&os=win" + str("&page=" + str(i))
        pass

    def headers(self):
        return {
            'Accept' : '*/*',
            'Accept-Encoding' : 'gzip, deflate',
            'Accept-Language' : 'zh-CN,zh;q=0.9',
            'Connection' : 'keep-alive',
            'User-Agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36',
        }

    

    





def get_text(url):
    try:
        headers = {
    
            "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/85.0.4183.102 Safari/537.36', 'Accept-Language': 'zh-CN '
        }
        r = requests.get(url, headers=headers)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        return r.text
    except:
        return "爬取网站失败！"


def run(game_info, jump_link, game_evaluation, text):
    soup = BeautifulSoup(text, "html.parser")

    # 游戏评价
    w = soup.find_all(class_="col search_reviewscore responsive_secondrow")
    for u in w:
        if u.span is not None:
            game_evaluation.append(
                u.span["data-tooltip-html"].split("<br>")[0] + "," + u.span["data-tooltip-html"].split("<br>")[-1])
        else:
            game_evaluation.append("暂无评价！")

    # 游戏详情页面链接
    link_text = soup.find_all("div", id="search_resultsRows")
    for k in link_text:
        b = k.find_all('a')
    for j in b:
        jump_link.append(j['href'])

    # 名字和价格
    global num
    name_text = soup.find_all('div', class_="responsive_search_name_combined")
    for z in name_text:
        # 每个游戏的价格
        name = z.find(class_="title").string.strip()
        # 判断折扣是否为None，提取价格
        if z.find(class_="col search_discount responsive_secondrow").string is None:
            price = z.find(class_="col search_price discounted responsive_secondrow").text.strip().split("¥")
            game_info.append([num + 1, name, price[2].strip(), game_evaluation[num], jump_link[num]])
        else:
            price = z.find(class_="col search_price responsive_secondrow").string.strip().split("¥")
            game_info.append([num + 1, name, price[1], game_evaluation[num], jump_link[num]])
        num = num + 1


def save_data(game_info):
    save_path = "./Steam.csv"
    df = pd.DataFrame(game_info, columns=['排行榜', '游戏名字', '目前游戏价格¥', '游戏评价', '游戏页面链接'])
    df.to_csv(save_path, index=0)
    print("文件保存成功！")




def init():
    log.init()
    sdbc = SqliteDBC(env.DB_PATH)
    sdbc.exec_script(env.SQL_PATH)



if __name__ == "__main__":
    init()
    

    # Game_info = []          # 游戏全部信息
    # Turn_link = []          # 翻页链接
    # Jump_link = []          # 游戏详情页面链接
    # Game_evaluation = []    # 游戏好评率和评价
    # for i in range(1, 11):
    #     Turn_link.append("https://store.steampowered.com/search/?cc=CN&filter=globaltopsellers&page=1&os=win" + str("&page=" + str(i)))
    #     run(Game_info, Jump_link, Game_evaluation, get_text(Turn_link[i-1]))
    # save_data(Game_info)