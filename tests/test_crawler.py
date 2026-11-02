import unittest
import sqlite3
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch
from urllib.parse import parse_qs, urlsplit

import requests

import main
from src.bean.t_steam_game import TSteamGame
from src.core import saver
from src.core.steam_crawler import SteamCrawler
from src.utils import num


FIXTURES = Path(__file__).with_name('fixtures')


def product(app_id, price, review=''):
    return ('<a class="extra search_result_row" href="https://store.steampowered.com/app/%s/">'
            '<span class="title">Example</span><img src="image.jpg">%s%s</a>'
            % (app_id, price, review))


class CrawlerTests(unittest.TestCase):
    def setUp(self):
        self.crawler = SteamCrawler('https://store.steampowered.com/search/')

    def test_current_search_snapshot(self):
        games = self.crawler.parse_game((FIXTURES / 'search_current.html').read_text(encoding='utf-8'))
        self.assertEqual(len(games), 2)
        game = games[1326470]
        self.assertEqual((game.original_price, game.discount_price, game.discount_rate),
                         ('¥108.00', '¥30.24', 72))
        self.assertEqual((game.evaluation, game.evaluation_id), ('特别好评', 8))
        self.assertIn('32678', game.evaluation_info)

    def test_current_rank_snapshot(self):
        games = self.crawler.parse_rank((FIXTURES / 'rank_current.html').read_text(encoding='utf-8'))
        self.assertEqual(len(games), 2)
        game = games[730]
        self.assertEqual((game.game_name, game.rank_id), ('Counter-Strike 2', 1))
        self.assertEqual((game.cur_player_num, game.today_max_player_num), (440245, 1288020))

    def test_legacy_discount_markup(self):
        html = product(1, '<div class="search_discount"><span>-75%</span></div>'
                          '<div class="search_price discounted"><span><strike>¥ 100</strike>'
                          '</span><br>¥ 25</div>')
        game = self.crawler.parse_game(html)[1]
        self.assertEqual((game.original_price, game.discount_price, game.discount_rate),
                         ('¥ 100', '¥ 25', 75))

    def test_paid_free_and_unavailable_items(self):
        html = product(1, '<div class="discount_final_price">¥99.00</div>')
        html += product(2, '<div class="discount_final_price">免费开玩</div>')
        html += product(3, '<div data-discount="100"><div class="discount_original_price">¥99.00</div>'
                           '<div class="discount_final_price">¥0.00</div></div>')
        html += product(4, '')
        games = self.crawler.parse_game(html)
        self.assertEqual(set(games), {1, 2, 3})
        self.assertEqual((games[1].original_price, games[1].discount_rate), ('¥99.00', 0))
        self.assertEqual((games[2].discount_price, games[2].discount_rate), ('0', 0))
        self.assertEqual((games[3].discount_price, games[3].discount_rate), ('0', 100))

    def test_mixed_negative_and_single_line_reviews(self):
        for label, score, style in [('褒贬不一', 5, 'mixed'), ('特别差评', 2, 'negative')]:
            with self.subTest(label=label):
                review = ('<span class="search_review_summary %s" '
                          'data-tooltip-html="%s&lt;br/&gt;1,234 reviews"></span>' % (style, label))
                game = self.crawler.parse_game(product(1, '<div class="search_price">¥ 20</div>', review))[1]
                self.assertEqual((game.evaluation_id, game.evaluation_info), (score, '1234 reviews'))
        review = '<span class="search_review_summary" data-tooltip-html="好评"></span>'
        self.assertEqual(self.crawler.parse_game(product(1, '<div class="search_price">Free</div>', review))[1].evaluation_id, 6)

    def test_bundle_id_comes_from_url(self):
        html = product(1, '<div class="discount_final_price">¥99</div>')
        html = html.replace('/app/1/', '/bundle/123/').replace('class="extra', 'data-ds-appid="1,2" class="extra')
        self.assertIn(123, self.crawler.parse_game(html))

    def test_legacy_rank(self):
        html = ('<div class="player_count_row"><a class="gameLink" href="https://store.steampowered.com/app/10/">Game</a>'
                '<span class="currentServers">1,234</span><span class="currentServers">5,678</span></div>')
        game = self.crawler.parse_rank(html)[10]
        self.assertEqual((game.rank_id, game.cur_player_num, game.today_max_player_num), (1, 1234, 5678))

    def test_invalid_response_is_not_an_empty_success(self):
        for parse in [self.crawler.parse_game, self.crawler.parse_rank]:
            with self.assertRaises(ValueError):
                parse('<html>Access denied</html>')
        self.assertEqual(self.crawler.parse_game('<div id="search_resultsRows"></div>'), {})

    @patch('src.core.steam_crawler.requests.get')
    def test_http_proxy_timeout_encoding_and_errors(self, get):
        response = requests.Response()
        response.status_code = 200
        response._content = '特别好评 ¥99'.encode('utf-8')
        response.encoding = 'ISO-8859-1'
        get.return_value = response
        proxy = {'https': 'http://127.0.0.1:8080'}
        crawler = SteamCrawler('https://store.steampowered.com/search/?cc=CN', proxy=proxy,
                               options={'specials': 0})
        self.assertEqual(crawler.get_html(), '特别好评 ¥99')
        self.assertEqual(get.call_args.kwargs['proxies'], proxy)
        self.assertEqual(get.call_args.kwargs['timeout'], (10, 30))
        query = parse_qs(urlsplit(crawler.url).query)
        self.assertEqual(query['specials'], ['0'])
        self.assertEqual(query['l'], ['schinese'])
        response.status_code = 503
        with self.assertRaises(requests.HTTPError):
            crawler.get_html()

    def test_options_are_not_mutated(self):
        options = {'cc': 'CN'}
        SteamCrawler('https://store.steampowered.com/search/', page=2, options=options)
        self.assertEqual(options, {'cc': 'CN'})

    def test_valid_unicode_title_is_not_discarded(self):
        html = product(1, '<div class="discount_final_price">¥99</div>').replace('Example', 'Ångström åäö')
        self.assertIn(1, self.crawler.parse_game(html))


class UpdateTests(unittest.TestCase):
    def test_failed_write_rolls_back_rank_reset(self):
        with tempfile.TemporaryDirectory() as folder:
            db = str(Path(folder) / 'steam.db')
            conn = sqlite3.connect(db)
            conn.executescript((FIXTURES.parent.parent / 'script/steam-create.sql').read_text(encoding='utf-8'))
            conn.execute('INSERT INTO t_steam_game (i_game_id,i_rank_id) VALUES (1,99)')
            conn.commit()
            conn.close()
            game = TSteamGame()
            game.game_id, game.game_name = 2, object()  # Unsupported SQLite value.
            with patch.dict(saver.config.settings.database, {'dbpath': db}):
                with self.assertRaises(sqlite3.ProgrammingError):
                    saver.to_db({2: game}, True, False)
            conn = sqlite3.connect(db)
            self.assertEqual(conn.execute('SELECT i_game_id,i_rank_id FROM t_steam_game').fetchall(), [(1,99)])
            conn.close()

    def test_sqlite_updates_existing_records_and_rank(self):
        with tempfile.TemporaryDirectory() as folder:
            db = str(Path(folder) / 'steam.db')
            with sqlite3.connect(db) as conn:
                conn.executescript((FIXTURES.parent.parent / 'script/steam-create.sql').read_text(encoding='utf-8'))
                conn.execute('INSERT INTO t_steam_game (i_game_id,s_game_name,s_original_price,s_lowest_price,'
                             's_discount_price,i_discount_rate,i_rank_id) VALUES (1,?,?,?,?,?,?)',
                             ('Old', '¥100', '¥80', '¥100', 0, 99))
            conn.close()
            game = TSteamGame()
            game.game_id, game.game_name = 1, 'Updated'
            game.original_price, game.discount_price, game.lowest_price = '¥100', '¥50', '¥50'
            game.discount_rate = 50
            game.evaluation_id, game.evaluation = 5, '褒贬不一'
            with patch.dict(saver.config.settings.database, {'dbpath': db}):
                saver.to_db({1: game}, False, True)
                game.rank_id, game.cur_player_num, game.today_max_player_num = 1, 1234, 5678
                saver.to_db({1: game}, True, False)
            with sqlite3.connect(db) as conn:
                row = conn.execute('SELECT s_discount_price,i_discount_rate,i_evaluation_id,i_rank_id,'
                                   'i_cur_player_num,i_today_max_player_num FROM t_steam_game WHERE i_game_id=1').fetchone()
                self.assertEqual(num.byte_to_str(row[0]), '¥50')
                self.assertEqual(row[1:], (50, 5, 1, 1234, 5678))
                self.assertEqual(conn.execute('SELECT count(*) FROM t_steam_game').fetchone()[0], 1)
            conn.close()

    def test_price_grouping_does_not_corrupt_lowest_price(self):
        for price in ['¥1,299.99', '€1.299,99', '1 299,99 €']:
            with self.subTest(price=price):
                self.assertEqual(num.to_float(price), 1299.99)
        self.assertEqual(num.to_float('¥1,299'), 1299)

    @patch('src.core.saver.sqlite3.connect')
    def test_empty_rank_does_not_clear_cache(self, database):
        saver.to_db({}, True, False)
        database.assert_not_called()

    def test_free_and_unreviewed_update_clears_old_values(self):
        old, new = TSteamGame(), TSteamGame()
        old.original_price = '¥99'
        old.lowest_price = '¥50'
        old.evaluation_id, old.evaluation = 8, '特别好评'
        new.original_price = new.discount_price = new.lowest_price = '0'
        new.discount_rate = 0
        new.evaluation, new.evaluation_info = '暂无评价', ''
        saver.compare(old, new, False, True)
        self.assertEqual((old.original_price, old.lowest_price, old.discount_rate), ('0', '0', 0))
        self.assertIsNone(old.evaluation_id)

    @patch('main.pager.to_page')
    @patch('main.update_random_discount')
    @patch('main.update_top_discount', return_value=0)
    @patch('main.update_rank', return_value=False)
    def test_total_failure_does_not_regenerate_pages(self, rank, top, random, page):
        with self.assertRaises(RuntimeError):
            main.main({}, 1, 'CN', True, '', 10)
        page.assert_not_called()

    @patch('main.saver.to_db')
    @patch('main.SteamCrawler')
    def test_failed_rank_is_not_saved(self, crawler, save):
        crawler.return_value.get_html.side_effect = requests.Timeout('timeout')
        self.assertFalse(main.update_rank({}))
        save.assert_not_called()


if __name__ == '__main__':
    unittest.main()
