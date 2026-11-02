import csv
import io
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from PIL import Image

from src.bean.t_steam_game import TSteamGame
from src.core import archive, assets


class StorageTests(unittest.TestCase):
    def test_every_low_survives_without_full_catalog(self):
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            old = base / 'old.db'
            schema = (Path(__file__).resolve().parents[1] / 'script/steam-create.sql').read_text(encoding='utf-8')
            conn = sqlite3.connect(old)
            conn.executescript(schema)
            conn.executemany('INSERT INTO t_steam_game (i_game_id,s_lowest_price) VALUES (?,?)',
                             [(1, '¥9.90'), (2, '0'), (3, b'$1.99'), (4, None)])
            conn.commit()
            conn.close()
            with patch.dict(archive.settings.database, {'dbpath': str(old)}):
                archive.save(page_ids=set())
            with (base / 'lowest-prices.csv').open(encoding='utf-8') as source:
                self.assertEqual(len(list(csv.DictReader(source))), 4)
            new = base / 'new.db'
            conn = sqlite3.connect(new)
            conn.executescript(schema)
            conn.close()
            with patch.dict(archive.settings.database, {'dbpath': str(new)}):
                archive.restore()
            conn = sqlite3.connect(new)
            self.assertEqual(conn.execute('SELECT i_game_id,s_lowest_price FROM t_steam_game ORDER BY i_game_id').fetchall(),
                             [(1, '¥9.90'), (2, '0'), (3, '$1.99'), (4, None)])
            conn.close()


class AssetTests(unittest.TestCase):
    def game(self):
        game = TSteamGame()
        game.game_id, game.shop_url = 10, 'https://store.steampowered.com/app/10/'
        game.img_url = 'https://example.com/cover.jpg'
        return game

    def test_cover_is_small_webp(self):
        with tempfile.TemporaryDirectory() as folder:
            source = io.BytesIO()
            Image.new('RGB', (460, 215), '#80a030').save(source, 'JPEG')
            response = Mock(content=source.getvalue())
            with patch.object(assets, 'ROOT', Path(folder)), patch.object(assets.requests, 'get', return_value=response):
                assets._cover(self.game())
                target = Path(folder) / 'docs/imgs/covers/app-10.webp'
                with Image.open(target) as image:
                    self.assertEqual((image.format, image.size), ('WEBP', (176, 66)))
                self.assertLess(target.stat().st_size, len(source.getvalue()))

    def test_region_does_not_invent_worldwide_availability(self):
        response = Mock(text='<div class="game_area_purchase_game"><div class="game_purchase_price">¥99</div></div>')
        response.url = self.game().shop_url
        with patch.object(assets, '_regions', {}), patch.object(assets, '_zone', 'CN'), patch.object(assets.requests, 'get', return_value=response):
            assets._region(self.game())
            label, notice = assets.region_label(self.game())
            self.assertEqual(label, '国区可购')
            self.assertIn('未披露跨区', notice)
            response.text = '该物品在您所在的地区不可用'
            assets._region(self.game())
            self.assertEqual(assets.region_label(self.game())[0], '国区不可购')


if __name__ == '__main__':
    unittest.main()
