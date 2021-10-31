#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author : EXP
# -----------------------------------------------

import sys
import time
from pypdm.dbc._sqlite import SqliteDBC
from src.cfg import env
from src.crawler.steam_crawler import SteamCrawler
from src.utils import log



def main(is_help, pages, cc, specials, filter) :
    for page in range(1, pages + 1) :
        sc = SteamCrawler(env.STEAM_GAME_PRICE_URL, page, options={
            'cc': cc,
            'specials': 1 if specials else 0,
            'filter': filter
        })
        html = sc.get_html()
        tsgs = sc.parse(html)

        for tsg in tsgs.values() :
            print('=========================')
            print(tsg)
        time.sleep(1)

    



def init() :
    log.init()
    sdbc = SqliteDBC(env.DB_PATH)
    sdbc.exec_script(env.SQL_PATH)


def sys_args(sys_args) :
    is_help = False
    pages = 10          # 爬取页数
    cc = 'CN'           # 价格区域
    specials = False    # 仅特惠游戏
    filter = 'globaltopsellers'    # 全球热销游戏
    
    idx = 1
    size = len(sys_args)
    while idx < size :
        try :
            if sys_args[idx] == '-h' or sys_args[idx] == '--help' :
                is_help = True
                break

            elif sys_args[idx] == '-p' :
                idx += 1
                pages = int(sys_args[idx])

            elif sys_args[idx] == '-z' :
                idx += 1
                cc = int(sys_args[idx])

            elif sys_args[idx] == '-s' or sys_args[idx] == '--specials' :
                idx += 1
                specials = sys_args[idx]

            elif sys_args[idx] == '-f' :
                idx += 1
                filter = sys_args[idx]

        except :
            pass
        idx += 1
    return is_help, pages, cc, specials, filter


if __name__ == "__main__" :
    init()
    try :
        main(*sys_args(sys.argv))
    except :
        log.error('未知异常')


    # Game_info = []          # 游戏全部信息
    # Turn_link = []          # 翻页链接
    # Jump_link = []          # 游戏详情页面链接
    # Game_evaluation = []    # 游戏好评率和评价
    # for i in range(1, 11):
    #     Turn_link.append("https://store.steampowered.com/search/?cc=CN&filter=globaltopsellers&page=1&os=win" + str("&page=" + str(i)))
    #     run(Game_info, Jump_link, Game_evaluation, get_text(Turn_link[i-1]))
    # save_data(Game_info)



# num = 0

# def get_text(url):
#     try:
#         headers = {
    
#             "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
#                           'Chrome/85.0.4183.102 Safari/537.36', 'Accept-Language': 'zh-CN '
#         }
#         r = requests.get(url, headers=headers)
#         r.raise_for_status()
#         r.encoding = r.apparent_encoding
#         return r.text
#     except:
#         return "爬取网站失败！"


# def run(game_info, jump_link, game_evaluation, text):
#     soup = BeautifulSoup(text, "html.parser")

#     # 游戏评价
#     w = soup.find_all(class_="col search_reviewscore responsive_secondrow")
#     for u in w:
#         if u.span is not None:
#             game_evaluation.append(
#                 u.span["data-tooltip-html"].split("<br>")[0] + "," + u.span["data-tooltip-html"].split("<br>")[-1])
#         else:
#             game_evaluation.append("暂无评价！")

#     # 游戏详情页面链接
#     link_text = soup.find_all("div", id="search_resultsRows")
#     for k in link_text:
#         b = k.find_all('a')
#     for j in b:
#         jump_link.append(j['href'])

#     # 名字和价格
#     global num
#     name_text = soup.find_all('div', class_="responsive_search_name_combined")
#     for z in name_text:
#         # 每个游戏的价格
#         name = z.find(class_="title").string.strip()
#         # 判断折扣是否为None，提取价格
#         if z.find(class_="col search_discount responsive_secondrow").string is None:
#             price = z.find(class_="col search_price discounted responsive_secondrow").text.strip().split("¥")
#             game_info.append([num + 1, name, price[2].strip(), game_evaluation[num], jump_link[num]])
#         else:
#             price = z.find(class_="col search_price responsive_secondrow").string.strip().split("¥")
#             game_info.append([num + 1, name, price[1], game_evaluation[num], jump_link[num]])
#         num = num + 1


# def save_data(game_info):
#     save_path = "./Steam.csv"
#     df = pd.DataFrame(game_info, columns=['排行榜', '游戏名字', '目前游戏价格¥', '游戏评价', '游戏页面链接'])
#     df.to_csv(save_path, index=0)
#     print("文件保存成功！")